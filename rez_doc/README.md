TODO:

- Remove the need to make a resolved context, if the user is already in a valid context!
- Check variants for missing linking. Not just the requires of a package
- Make sure that it only says intersphinx error for things that we can actually find URLs for
- Make sure to check for missing intersphinx mapping URLs. Not just mappings
- This should work with new style AND old style intersphinx mappings
- Make sure there are test results (both for check and fix) that have NO intersphinx_mapping defined at all
- Do a unittest for the --add-rez-requirements flag
- Add example command-line use


# rez-documentation-check

A tool that checks for missing intersphinx mappings for Rez packages
that use Sphinx documentation.

If any of that didn't make sense, here's some links to the terminology:

- [Rez](https://github.com/nerdvegas/rez)
- [Sphinx](https://www.sphinx-doc.org/en/master/usage/quickstart.html)
- [intersphinx](https://www.sphinx-doc.org/en/master/usage/extensions/intersphinx.html)


Basically, the goal of "intersphinx" is make documentation linkable
between different Sphinx projects. And ``rez_documentation_check`` helps
enforce this, but for Rez packages.


## How It Works

The steps that this tool does can be summarized like this:

- Check the current Rez package's list of requirements
- If a requirement has documentation, tell the user that
  they need to add an intersphinx link
- Check that each found URL exists, as well

And that's it.


## How To Run
### From A Shell

```sh
cd {some_rez_package_folder} && rez-env rez_documentation_check -- rez_documentation_check
```

> ``rez_documentation_check`` runs faster if you modify
> the ``rez-env`` command to include the Rez package plus
> ``rez_documentation_check``. Like ``rez-env some_package-1
> rez_documentation_check``


### From rez-test

Add this to your Rez package's package.py file


```python
tests = {
	"rez_documentation_check": {
		"command": "rez_documentation_check",
		"requires": ["rez_documentation_check"],
	},
}
```

Now rez-test will report any time you have out-of-date intersphinx links.
