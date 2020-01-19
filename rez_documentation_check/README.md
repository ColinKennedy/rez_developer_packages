
TODO:

- Make sure to check for missing intersphinx mapping URLs. Not just mappings
- Add example command-line use
- Update this README.md with new information


# rez-documentation-check

A tool that checks for missing intersphinx mappings for Rez packages
that use Sphinx documentation.

Some terminology:

- [Rez](https://github.com/nerdvegas/rez)
- [Sphinx](https://www.sphinx-doc.org/en/master/usage/quickstart.html)
- [intersphinx](https://www.sphinx-doc.org/en/master/usage/extensions/intersphinx.html)


## How It Works

The steps that this tool does can be summarized like this:

- Check the current Rez package's list of requirements
- If a requirement exists that has documentation, tell the user that
  they need to add an intersphinx link


## Where The Intersphinx Mapping Data Comes From

In short, it comes from Python imports. This logic is fairly well tested
so that, no matter how complex your Python code is, imports will always
be found. e.g. even if your Python file looks like this:

```python
for _ in range(10):
	if blah:
		try:
			from foo import bar
		except Exception:
			pass
```

``rez-documentation-check`` will still pick up "foo.bar". As long as
"foo.bar" points to a valid Python module **and** that module's package
has registered documentation, it should get included in the final output.

You also have the option to include Rez package dependencies as
intersphinx data, if you're prefer to not just check for Python imports.


TODO - Remove api.py


TODO check which if these dependencies are actually still in-use

```sh
rez-bind rez
rez-pip parso
rez-pip six
rez-pip wurlitzer
```
