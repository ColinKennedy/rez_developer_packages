
TODO:

- Check variants for missing linking. Not just the requires of a package
- Make sure to check for missing intersphinx mapping URLs. Not just mappings
- This should work with new style AND old style intersphinx mappings
- Make sure there are test results (both for check and fix) that have NO intersphinx_mapping defined at all
- Add example command-line use


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
- If a requirement has documentation, tell the user that
  they need to add an intersphinx link
- Check that each found URL exists, as well

And that's it.
