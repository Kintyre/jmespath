# JMESPath for Splunk

JMESPath (pronounced "james path") allows you to declaratively specify how to extract elements from a JSON document.

Splunk users can download and install the app from [SplunkBase](https://splunkbase.splunk.com/app/3237/).
Developers can access the full source code on [GitHub](https://github.com/Kintyre/jmespath).

Checkout the collection of [jmespath example searches](https://github.com/Kintyre/jmespath/wiki/jmsepath-search-examples) in the docs.

## Syntax

    jmespath (jmespath-string) [field=(field)] [outfield=(field)] [default=(string)]

## Examples

For example, given this document:

```json
{"foo": {"bar": "baz"}}
```
The jmespath expression `foo.bar` will return "baz".

JMESPath also supports:

Referencing elements in a list. Given the data:

```json
{"foo": {"bar": ["one", "two"]}}
```
The expression: `foo.bar[0]` will return "one". You can also reference all the items in a list using the `*` syntax:

```json
{"foo": {"bar": [{"name": "one"}, {"name": "two"}]}}
```
The expression: `foo.bar[*].name` will return `["one", "two"]`. Negative indexing is also supported (-1 refers to the last element in the list). Given the data above, the expression `foo.bar[-1].name` will return "two".

The `*` can also be used for hash types:

```json
{"foo": {"bar": {"name": "one"}, "baz": {"name": "two"}}}
```
The expression: `foo.*.name` will return `["one", "two"]`.


## Output modes

The `jmmespath` search command has two different modes for handling output variables:  A named field or a wild carded field pattern.

With a named output field only that specific field is updated.  If the result of the evaluated `<jmespath-string>` is a complex object, then a JSON formatted string is returned instead of raw value.  This preserves data accuracy and allow for multistep processing when necessary.

When a wildcarded output field is given, multiple output fields are be created using the wildcard as a field template or pattern.  In this case, it's necessary for the jmespath search command to assume that the result of the query expression will result in a hash (object) rather than a single value or array.  The hash keys will be combined with the given output pattern to make the final output field names.  The number of fields that will be created, depends completely on your data.

### Example

The following example demonstrates the different means of using the `output` field for the same given

Json input:
```json
{ "colors" :
    {
        "apple" : "yellow",
        "snake" : "black",
        "foobar" : "brown"
    }
}
```

Assuming the expression

    ... | jmespath input=j OUTPUT-OPTION "colors"

| *OUTPUT-OPTION* | *field(s) created* | *notes* |
| ----------------- | ------------------ | ------- |
| `output=colors`   | `colors`={ "apple": "yellow", "snake": "black", "foobar" : "brown" } | Simple static output.  The output is converted back to JSON since value is structured. |
| `output=color.*`  | `color.apple`=yellow, `color.snake`=black, `color.foobar`=brown | The `color.` prefix is applied to all keys. |
| `output=*_color`  | `apple_color`=yellow, `snake_color`=black, `foobar_color`=brown | The `_color` suffix is applied to all keys. |
| `output=*`        | `apple`=yellow, `snake`=black, `foobar`=brown | Keys are used as is.  Note this could overwrite existing fields if they are already present. |

A few takeaways:

 * The static output makes it easy for subsequent processing with additional `jmespath` or `spath` commands
 * Prefix and suffix approaches allow fields to be easily grouped with other wildcard capable search commands.  For example:  `stats values(color.*) as color.* by ...`, and they can all be cleaned up all at once using `| fields - color.*`.  This technique helps when taming exotic or erratic json objects.
 * The behavior of `output=*` is generally similar to `spath` behavior however jmespath output only unwraps a single level.  That is  `{ "a": { "b": { "c": 1}}}` would return as `a.b`=`{"c":1}` for `jmespath`, where as `spath` would return `a.b.c` = `1`.  While this may seem less-helpful for this simple scenario, it's a feature!  Because consider what happens when `c` is a complex JSON object, rather than the number 1.  (And if you'd prefer to get `a.b.c`, then just use `spath`.)

### Other notes

In wildcared mode, if a non-hash object is returned by your expression, then the output field will contain the word `anononymous` instead of a key name.  This seemed like a better option than dropping the data or using the literal `output` values, since it contains a `*` character.

The `jmsepath` search command will attempt to sanitize key names that are inappropriate for Splunk field names.  This could result in data loss (if your data contains both the keys "My Field" and "My-Field" in the same hash) and things like dots (`.`) in your field name could be handled in ways that aren't idea.  If you have thoughts on how to do it better, feel free to send bug reports and feature requests!  Pull requests welcome!

## What is this JMESPath?

JMESPath is used prominently in a few other projects/tools that you have already used:

 * [AWS CLI --query][jp-example-aws] option reduces the need for external JSON processing
 * [Ansible json_query()][jp-example-ansible] filters allow for complex structures to be converted into simple loops
 * [jp][jp-example-jp] CLI tool is the command line interface for JMESPath.  (Not to be confused with `jq`, which uses a different syntax.)

More information can be found here http://jmespath.org/

Live Tutorials here:
http://jmespath.org/tutorial.html


## Quoting

Special care is needed for keys that contain unusual characters or symbols that interfere with the JMESPath syntax.  Fortunately, this isn't a problem for many json docs.  But when it is, simply wrapping the token in question in double quotes.  Keep in mind that since the entire `<jmespath-string>` is often already quoted to keep JMESPath and Splunk syntax separate, so the JMESPath double quotes themselves must be escaped.  Don't worry.  It's not that bad, take a look:

Take an example, a json doc like this:

```json
{ "doc" : { "og:site_name": "LA Weekly" } }
```

If you want to pull out the `og:site_name` value, use a command like so:

    ... | jmespath output=site "doc.\"og:site_name\""

Without the double quotes, the `:` character would cause a parsing error.


## Support

Community support is available on best-effort basis only.  For information about commercial support, contact [Kintyre](mailto:hello@kintyre.co)
Issues are tracked via [GitHub](https://github.com/Kintyre/jmespath/issues)

## History

### 1.9.4 (Nov 14, 2018) Fourth public 2.0 release candidate
 * Fix bug with mvlist inputs.  (More of a just-dont-crash-workaround for the moment).
 * Enhance output so that mvfields are only used as needed.   Also eliminated the scenario where a single value could be unnecessarily wrapped in a single item list
and therefore be returned as a JSON string.

### 1.9.3 (Nov 13, 2018) Third public 2.0 release candidate
  * Adds wildcard support for the `output` argument.  This allows hashes to be expanded into multiple output fields in one invocation to `jmespath`
  * Fixed bug in the `unroll()` function.
  * Added support for quoting within the JMESpath expression, thus allowing support for keys that contain symbols.

### 1.9.2 (Nov 13, 2018) Second public 2.0 release candidate
  * Adds secondary search command:  `jsonformat`  This supports formatting JSON events and/or fields, syntax validation, control over key ordering and so on.  (Also contains an Easter egg where it can convert a python repr string into a valid JSON object, helpful for debugging splunklib searchcommand logs.)
  * Adds the Splunk Python SDK (1.6.5) for use with `jsonformat` and eventually `jmespath`.

### 1.9.1 (Nov 12, 2018) First public 2.0 release candidate
  * Add several custom functions to JMESPath core to simplify common Splunk data scenarios.
  * *BREAKING CHANGE*:  Switched to use `spath` style arguments instead of `xpath` style.  (Technically a compatibility layer is in place, but I'm hoping not to keep that around too long.)
  * Ensure that complex results are always returned as a JSON string, not as a python representation format.  This allows subsequent processing with less hassle.
  * Significant expansion of docs and UI feedback.


### 1.0.2 (Nov 9, 2018) - Added logo
  * Add appIcon images to avoid AppInspect violations

### 1.0.1 (Nov 9, 2018) - Lowell's first release (stability of existing code)
  * Upgraded jmsepath python library to 0.9.3
  * Added error reporting for JMESpath errors (JSON decoding errors are still silently ignored)
  * Fixed bug where 'default' would overwrite query output
  * Add inline help and hints to the UI (searchbnf)

### 1.0 RC2 (July 26, 2016) - Pre-release by John Berwick
  * Add flatten procedure

### 1.0 RC (July 24, 2016) - Pre-release by John Berwick
  * First public release


## Credits

 * John Berwick: the original author of this Splunk app
 * James Saryerwinnie:  author of [JMESPath](https://pypi.org/project/jmespath/) Python library
 * Mike Rybar: Logo

[jp-example-ansible]: https://docs.ansible.com/ansible/2.7/user_guide/playbooks_filters.html#json-query-filter
[jp-example-aws]: https://docs.aws.amazon.com/cli/latest/userguide/controlling-output.html#controlling-output-filter
[jp-example-jp]: https://github.com/jmespath/jp
