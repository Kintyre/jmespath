#   Version 1.0
import splunk.Intersplunk as si
import json, os, sys, itertools
import sys
from itertools import chain

ERROR_FIELD = "_jmespath_error"

DIR = os.path.dirname(__file__)
sys.path.append(os.path.join(DIR, "lib"))

import jmespath
from jmespath.exceptions import ParseError, JMESPathError, UnknownFunctionError

def flatten(container):
    if isinstance(container, (list,tuple)):
        for i in container:
            if isinstance(i, (list,tuple)):
                for j in flatten(i):
                    yield str(j)
            else:
                yield str(i)
    else:
        yield str(container)

if __name__ == '__main__':
    try:
        keywords,options = si.getKeywordsAndOptions()
        defaultval = options.get('default', None)
        field = options.get('field', '_raw')
        outfield = options.get('outfield', 'jpath')
        if len(keywords) != 1:
            si.generateErrorResults('Requires exactly one path argument.')
            sys.exit(0)
        path = keywords[0]

        try:
            jp = jmespath.compile(path)
        except ParseError as e:
            # Todo:  Consider stripping off the last line "  ^" pointing to the issue.
            # Not helpful since Splunk wrapps the error message in a really ugly way.
            si.generateErrorResults("Invalid JMESPath expression '{}'. {}".format(path,e))
            sys.exit(0)

        results,dummyresults,settings = si.getOrganizedResults()
        # for each results
        for result in results:
            # get field value
            ojson = result.get(field, None)
            added = False
            if ojson is not None:
                try:
                    json_obj = json.loads(ojson)
                except ValueError:
                    # Invalid JSON.  Move on, nothing to see here.
                    continue
                try:
                    values = jp.search(json_obj)
                    result[outfield] = list(flatten(values))
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
                result[outfield] = defaultval
        si.outputResults(results)
    except Exception as e:
        import traceback
        stack =  traceback.format_exc()
        si.generateErrorResults("Error '%s'. %s" % (e, stack))
