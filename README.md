# JMESPath for Splunk

JMESPath (pronounced "james path") makes dealing with JSON data in Splunk easier by leveraging a standardized query language for JSON.  This allows you to declaratively specify how to extract elements from a JSON document.  In many ways, this is a better `spath`.

Splunk users can download and install the latest release from [SplunkBase](https://splunkbase.splunk.com/app/3237/).
Developers can access and contribute to this app on [GitHub](https://github.com/Kintyre/jmespath).

## Syntax

    jmespath "<jmespath-string>" [input=<field>] [output=<field>] [default=<string>]
    jsonformat [indent=<int>] [order=undefined|preserve|sort] <field> [AS <field>]

## Documentation

Full documentation regarding this app, how to use it, along with various tips and tricks about how to best extract and format your JSON events is available on the GitHub wiki page.  See the official [JMESPath for Splunk documentation](https://github.com/Kintyre/jmespath/wiki/).  Many "run-anywhere" examples are provided throughout to help new users get a solid understanding of this tool.

## Installation & Configuration

See the [Install an add-on](https://docs.splunk.com/Documentation/AddOns/released/Overview/Singleserverinstall) in Splunk's official documentation.  There are no extra install steps.  No configuration is required.


## Support

Community support is available on best-effort basis.  For information about commercial support, contact [Kintyre](mailto:hello@kintyre.co).
Issues are tracked via [GitHub](https://github.com/Kintyre/jmespath/issues)

## History

See the full [Change log](https://github.com/Kintyre/jmespath/wiki/Change-Log)

## Credits

 * John Berwick: original author of this Splunk app
 * Lowell Alleman: current maintainer
 * James Saryerwinnie: author of [JMESPath](https://pypi.org/project/jmespath/) Python library
 * Mike Rybar: Logo

