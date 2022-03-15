import textwrap


rst_epilog = textwrap.dedent(
    """\
    .. _Sphinx conf.py: https://www.sphinx-doc.org/en/master/usage/configuration.html
    .. _build_requires: https://github.com/nerdvegas/rez/wiki/Package-Definition-Guide#build_requires
    .. _help: https://github.com/nerdvegas/rez/wiki/Package-Definition-Guide#help
    .. _index.rst: https://sphinx-tutorial.readthedocs.io/step-1
    .. _intersphinx: https://www.sphinx-doc.org/en/master/usage/extensions/intersphinx.html
    .. _intersphinx_mapping: https://www.sphinx-doc.org/en/master/usage/extensions/intersphinx.html
    .. _package help: https://github.com/nerdvegas/rez/wiki/Package-Definition-Guide#help
    .. _package.py: https://github.com/nerdvegas/rez/wiki/Package-Commands
    .. _package_preprocess_function: https://github.com/nerdvegas/rez/wiki/Configuring-Rez#package_preprocess_function
    .. _private_build_requires: https://github.com/nerdvegas/rez/wiki/Package-Definition-Guide#private_build_requires
    .. _requires: https://github.com/nerdvegas/rez/wiki/Package-Definition-Guide#requires
    .. _rez help attribute: https://github.com/nerdvegas/rez/wiki/Package-Definition-Guide#help
    .. _rez-build: https://github.com/nerdvegas/rez/wiki/Getting-Started#building-your-first-package
    .. _rez-config: https://github.com/nerdvegas/rez/wiki/Command-Line-Tools#rez-config
    .. _sphinx-apidoc: https://www.sphinx-doc.org/en/master/man/sphinx-apidoc.html
    .. _sphinx-quickstart: https://www.sphinx-doc.org/en/master/man/sphinx-quickstart.html
    .. _sphinx-rtd-theme: https://pypi.org/project/sphinx-rtd-theme/
    .. _sphinx.ext.autodoc: https://www.sphinx-doc.org/en/master/usage/extensions/autodoc.html
    .. _toctree: https://www.sphinx-doc.org/en/master/usage/restructuredtext/directives.html
    """
)

# TODO : Consider remove rez-config references

# TODO : Add these
# - build_documentation_key` - The rez_sphinx key information
# `objects.inv`_.
# - :ref:`rez_sphinx tag` - documentation to where I explain the ..
# - :ref:`rez_sphinx auto-help` -
# - :ref:`minimal bootstrapper`
