#JMESPath for Splunk

JMESPath (pronounced "james path") allows you to declaratively specify how to extract elements from a JSON document.

## Syntax

    jmespath <jmespath-string> [field=<field>] [outfield=<field>] [default=<string>]

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

## What is this JMESPath?

JMESPath is used prominently in a few other projects/tools that you have already used:

 * [AWS CLI --query][jp-example-aws] option reduces the need for external JSON processing
 * [Ansible json_query()][jp-example-ansible] filters allow for complex structures to be converted into simple loops
 * [jp][jp-example-jp] CLI tool is the command line interface for JMESPath.  (Not to be confused with `jq`, which uses a different syntax.)

More information can be found here http://jmespath.org/

Live Tutorials here:
http://jmespath.org/tutorial.html


## Support

Community support is available on best-effort basis only.  For information about commercial support, contact [Kintyre](mailto:sales@kintyre.co)


## History

 * 1.0.2 (Nov 9, 2018) - Added logo
   * Add appIcon images to avoid AppInspect violations

 * 1.0.1 (Nov 9, 2018) - Lowell's first release (stability of existing code)
   * Upgraded jmsepath python library to 0.9.3
   * Added error reporting for JMESpath errors (JSON decoding errors are still silently ignored)
   * Fixed bug where 'default' would overwrite query output
   * Add inline help and hints to the UI (searchbnf)

 * 1.0 RC2 (July 26, 2016) - Pre-release by John Berwick
   * Add flatten procedure

 * 1.0 RC (July 24, 2016) - Pre-release by John Berwick
   * First public release


## Credits

 * John Berwick: the original author of this Splunk app
 * James Saryerwinnie:  author of [JMESPath](https://pypi.org/project/jmespath/) Python library
 * Mike Rybar: Logo

[jp-example-ansible]: https://docs.ansible.com/ansible/2.7/user_guide/playbooks_filters.html#json-query-filter
[jp-example-aws]: https://docs.aws.amazon.com/cli/latest/userguide/controlling-output.html#controlling-output-filter
[jp-example-jp]: https://github.com/jmespath/jp
