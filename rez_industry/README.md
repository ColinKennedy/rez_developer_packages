A simple Python package that helps modify Rez package.py files.


## How To Use

```python
with open("/path/to/some/package.py", "r") as handler:
    code = handler.read()

new_code = api.add_to_attribute("help", {"foo": "bar"}, code)

with open("/path/to/some/package.py", "w") as handler:
    handler.write(new_code)
```


## Supported Rez Attributes

- [help](https://github.com/nerdvegas/rez/wiki/Package-Definition-Guide#help)
- [tests](https://github.com/nerdvegas/rez/wiki/Package-Definition-Guide#tests)

Anything that is considered valid input for these attributes can be
passed to ``add_to_attribute``.


## TODO

- Make sure that this fails if there's @early or @late
 - finding append assignments should still work even if there's @early / @late though

- Make the append logic try to "find" the right position to put the help / test data
 - Probably will need some kind of "recommended assignment order" to reference
