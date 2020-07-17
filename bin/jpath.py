import json
import re
import sys

import splunk.Intersplunk as si

ERROR_FIELD = "_jmespath_error"

import jmespath
from jmespath import functions
from jmespath.exceptions import ParseError, JMESPathError, UnknownFunctionError


# Custom functions for the JMSEPath language to make some typical splunk use cases easier to manage
class JmesPathSplunkExtraFunctions(functions.Functions):

    @functions.signature({'types': ['object']})
    def _func_items(self, h):
        """ JMESPath includes a keys() and a values(), but with unordered objects, there's no way
        to line these up!  So this feels like an pretty obvious extension to a Python guy! """
        return list(h.items())

    @functions.signature({'types': ['array']})
    def _func_to_hash(self, array):
        """ Send in an array of [key,value] pairs and build a hash.  If duplicates, the last value
        for 'key' wins.
        """
        h = {}
        for item in array:
            try:
                key, val = item
                h[key] = val
            except Exception:
                pass
        return h

    @functions.signature({'types': ['string', 'array']})
    def _func_from_string(self, s):
        """
        Possible name options:
            parse           Nice, but parse what?
            from_string     Parity with to_string (exports data AS a json string)
            from_json?      Maybe more clear?  not sure
            unnest          Can't get past the double "n"s
            jsonstr         My first option, but don't like it.
        """
        if s is None:
            return None
        if isinstance(s, (list,tuple)):
            return [ json.loads(i) for i in s ]
        try:
            return json.loads(s)
        except Exception:
            return s

    @functions.signature({'types': ['array']}, {'types':['string']}, {'types':['string']})
    def _func_unroll(self, objs, key, value):
        """ What to call this"?
            unroll
            zipdict     ?
            kvarray2hash    a bit long
            xyseries    haha
            table/untable
            make_hash
            unzip       Maybe
        """
        d = dict()
        for item in objs:
            try:
                k = item[key]
                v = item[value]
                if not isinstance(k, (str, unicode)):
                    k = str(k)
                k = sanitize_fieldname(k)
                # XXX: User option:  Overwrite, or make mvlist  (Possibly just make 2 different functions?)
                if k not in d:
                    d[k] = v
                else:
                    # Opportunistically turn this into a container to hold more than on value.
                    # Generally harmful to structured data, but plays nice with Splunk's mvfields
                    if not isinstance(d[k], list):
                        d[k] = [ d[k] ]
                    d[k].append(v)
            except KeyError:
                # If either field is missing, just silently move on
                continue
            except NameError:
                raise
            except Exception as e:
                # FOR DEBUGGING ONLY
                return "ERROR:  {}  key={} value={} in {}".format(e, key, value, item)
        return d


jp_options = jmespath.Options(custom_functions=JmesPathSplunkExtraFunctions())


def sanitize_fieldname(field):
    # XXX: Add caching, if needed
    clean = re.sub(r'[^A-Za-z0-9_.{}\[\]]', "_", field)
    # Remove leading/trailing underscores
    # It would be nice to preserve explicit underscores but don't want to complicate the code for
    # a not-yet-existing corner case.  Generally it's better to avoid hidden fields.
    clean = clean.strip("_")
    return clean


def flatten(container):
    if isinstance(container, dict):
        yield json.dumps(container)
    elif isinstance(container, (list,tuple)):
        for i in container:
            if isinstance(i, (list,tuple,dict)):
                yield json.dumps(i)
            else:
                yield str(i)
    else:
        yield str(container)


def output_to_field(values, output, record):
    content = list(flatten(values))
    if not content:
        content = None
        record[output] = None
    elif len(content) == 1:
        # Avoid the overhead of MV field encoding
        content = content[0]
    record[output] = content


def output_to_wildcard(values, output, record):
    output_template = output.replace("*", "{}", 1)
    if values is None:
        # Don't bother to make any fields
        return

    if isinstance(values, dict):
        for (key, value) in values.items():
            final_field = output_template.format(sanitize_fieldname(key))
            if isinstance(value, (list, tuple)):
                if not value:
                    value = None
                elif len(value) == 1:
                    # Unroll, to better match Splunk's default handling of mvfields
                    value = value[0]
                else:
                    value = json.dumps(value)
                record[final_field] = value
            elif isinstance(value, dict):
                record[final_field] = json.dumps(value)
            else:
                record[final_field] = value
    else:
        # Fallback to using a silly name since there's no hash key to work with.
        # (Maybe users didn't mean to use '*' in output, or possibly a record/data specific issue
        final_field = output_template.format("anonymous")
        record[final_field] = json.dumps(values)


def legacy_args_fixer(options):
    # Support legacy field names (xpath vs spath) field/outfield
    argmap = [
        ("input", "field"),
        ("output", "outfield"),
    ]
    for (n_arg, o_arg) in argmap:
        if o_arg in options and n_arg not in options:
            # XXX:  Write a warning somewhere!
            options[n_arg] = options[o_arg]


def jpath():
    try:
        keywords, options = si.getKeywordsAndOptions()
        legacy_args_fixer(options)

        defaultval = options.get('default', None)
        fn_input = options.get('input', options.get('field', '_raw'))
        fn_output = options.get('output', 'jpath')
        if len(keywords) != 1:
            si.generateErrorResults('Requires exactly one path argument.')
            sys.exit(0)
        path = keywords[0]

        # Handle literal (escaped) quotes.  Presumably necessary because of raw args?
        path = path.replace(r'\"', '"')

        if "*" in fn_output:
            apply_output = output_to_wildcard
        else:
            apply_output = output_to_field

        try:
            jp = jmespath.compile(path)
        except ParseError as e:
            # Todo:  Consider stripping off the last line "  ^" pointing to the issue.
            # Not helpful since Splunk wraps the error message in a really ugly way.
            si.generateErrorResults("Invalid JMESPath expression '{}'. {}".format(path, e))
            sys.exit(0)

        results, dummyresults, settings = si.getOrganizedResults()
        # for each results
        for result in results:
            # get field value
            ojson = result.get(fn_input, None)
            added = False
            if ojson is not None:
                if isinstance(ojson, (list, tuple)):
                    # XXX: Add proper support for multivalue input fields.  Just use first value for now
                    ojson = ojson[0]
                try:
                    json_obj = json.loads(ojson)
                except ValueError:
                    # Invalid JSON.  Move on, nothing to see here.
                    continue
                try:
                    values = jp.search(json_obj, options=jp_options)
                    apply_output(values, fn_output, result)
                    result[ERROR_FIELD] = None
                    added = True
                except UnknownFunctionError as e:
                    # Can't detect invalid function names during the compile, but we want to treat
                    # these like syntax errors:  Stop processing immediately
                    si.generateErrorResults("Issue with JMESPath expression. {}".format(e))
                    sys.exit(0)
                except JMESPathError as e:
                    # Not 100% sure I understand what these errors mean. Should they halt?
                    result[ERROR_FIELD] = "JMESPath error: {}".format(e)
                except Exception as e:
                    result[ERROR_FIELD] = "Exception: {}".format(e)

            if not added and defaultval is not None:
                result[fn_output] = defaultval

        si.outputResults(results)
    except Exception as e:
        import traceback

        stack = traceback.format_exc()
        si.generateErrorResults("Error '%s'. %s" % (e, stack))


if __name__ == '__main__':
    jpath()
