# jmespath

_JMESPath for Splunk_

## Example usage

JMESPath for Splunk implements a streaming custom SPL search command called `jsonformat`.

```
| jsonformat type=robot height=tall

| jsonformat action=ping target=fancy_pig
```


## Sourcetypes

| Sourcetype | Purpose |
| ---------- | ------- |
| command:jsonformat | Internal logs and stats related to custom Jmespath SPL command. |


## Troubleshooting

Find internal/script errors:

### Enable debug logging

Add `logging_level=DEBUG` to your existing query to enable additional debug logs:

```
| jsonformat logging_level=DEBUG query=...
```



### Search internal logs

Search the above debug logs, or other messages from or about the Jmespath SPL search command:
```
index=_internal (source=*jmespath.log*) OR (sourcetype=splunkd jsonformat.py)
```

Review SPL search command logs group by request:

```
index=_internal sourcetype=command:jsonformat | transaction host Pid
```

## License

## Development

If you would like to develop or build this TA from source, see the [development](./DEVELOPMENT.md) documentation.

## Reference

 * **API Docs**:  https://....


This addon was built from the [Kintyre Splunk App builder](https://github.com/Kintyre/cypress-cookiecutter) (version 1.11.2) [cookiecutter](https://github.com/audreyr/cookiecutter) project.
