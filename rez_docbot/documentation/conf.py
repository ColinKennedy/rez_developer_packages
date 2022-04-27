# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
# import os
# import sys
# sys.path.insert(0, os.path.abspath('.'))


# -- Project information -----------------------------------------------------

project = 'rez_docbot'
copyright = '2022, '
author = ''


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    'sphinx.ext.intersphinx',
]

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# The language for content autogenerated by Sphinx. Refer to documentation
# for a list of supported languages.
#
# This is also used if you do content translation via gettext catalogs.
# Usually you set "language" from the command line for these cases.
language = 'en'

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = 'alabaster'

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = []


# -- Extension configuration -------------------------------------------------

# -- Options for intersphinx extension ---------------------------------------

# Example configuration for intersphinx: refer to the Python standard library.
intersphinx_mapping = {'https://docs.python.org/3/': None}


# -- rez-sphinx start --
# -- DO NOT TOUCH --
#
# These lines are needed for rez-sphinx to work
#
from rez_sphinx import api

locals().update(api.bootstrap(locals()))
#
# If you want to add extra user customizations, please feel free to add any
# of them BELOW this line.
#
# -- rez-sphinx end --

import textwrap

html_theme = "sphinx_rtd_theme"
extensions.extend(("sphinx.ext.napoleon", "sphinx.ext.todo"))

intersphinx_mapping.update(
    {"https://docs.python.org/3/": None, "https://nerdvegas.github.io/rez": None}
)

rst_epilog = textwrap.dedent(
    """\
    .. _.gitignore: https://git-scm.com/docs/gitignore
    .. _.gitignore_global: https://docs.github.com/en/get-started/getting-started-with-git/ignoring-files
    .. _.nojekyll: https://github.blog/2009-12-29-bypassing-jekyll-on-github-pages/
    .. _CRUD: https://en.wikipedia.org/wiki/Create,_read,_update_and_delete
    .. _GitHub Enterprise: https://github.com/enterprise
    .. _GitHub access token: https://docs.github.com/en/enterprise-server@3.4/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token
    .. _GitHub organization: https://docs.github.com/en/organizations
    .. _GitHub: https://github.com
    .. _OPSEC: https://en.wikipedia.org/wiki/Operations_security
    .. _SemVer: https://semver.org
    .. _Sphinx: https://www.sphinx-doc.org/en/master
    .. _gh-pages: https://pages.github.com
    .. _git: https://git-scm.com/
    .. _package.py: https://github.com/nerdvegas/rez/wiki/Package-Commands
    .. _rezconfig.py: https://github.com/nerdvegas/rez/blob/fa3fff6f0b7b4b53bbb9baa4357ab42117d06356/src/rez/rezconfig.py
    """
)
