# rez-documentation-check

A tool that checks for missing intersphinx mappings for Rez packages
that use Sphinx documentation.

Some terminology:

- [Rez](https://github.com/nerdvegas/rez)
- [Sphinx](https://www.sphinx-doc.org/en/master/usage/quickstart.html)
- [intersphinx](https://www.sphinx-doc.org/en/master/usage/extensions/intersphinx.html)


## How It Works

The steps that this tool does can be summarized like this:

- Given some file / folder paths
- Find the Rez package that describes those paths
- If the Rez package is not installed (e.g. it's a source Rez package)
    - Build the package to a temporary location
- Search each of the given file / folder paths for Python files
- For each Python file, get every import statement
- Find every Python module that each import comes from
- If the module comes from a recognizable Rez package or Python package
    - Get the package's name
- Search for a documentation URL that matches that package's name
- Format the package + URL data as intersphinx data
- Print the intersphinx data or write it to-disk


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


## Using this package from Python

Check out [api.py](python/rez_documentation_check/api.py). It has all of
the "public" functions that you can use.


## Install

Every requirement of this package can be installed using standard Rez
commands if you don't already have the packages sourced, yourself.

```sh
rez-bind rez
rez-pip parso
rez-pip six
rez-pip wurlitzer
```
