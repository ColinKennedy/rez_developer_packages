- Add README.rst in the auto-generated api folder
- Make sure the readthedocs.io theme can be added, via ``rez-config`` settings

- On-build
 - Check if any pages are still defaults. And fail early
  - Add an option to disable this feature

- config subparser
 - print a default configuration for the user
  - as yaml
  - as python?


- Rez ``help`` conversion

- Need unittest so you cannot accidentally add the same file twice to the same toctree


- Check what sphinx.ext.githubpages is!!


"init_options": {
	"default_files": [
		{
			"sphinx_title": "User Documentation",
			"file_name": "user_documentation",  # suffix is auto-added
			"default_text": "blah blah",
			"check_pre_build": True,
			"add_rez_sphinx_tag": True,
		},
		{
			"sphinx_title": "Developer Documentation",
			"file_name": "developer_documentation",  # suffix is auto-added
			"default_text": "blah blah",
			"check_pre_build": True,
		},
	]
}

- Auto-discover python code based on the appends to PYTHONPATH

init
 ---add-remote
 - add the ability to add a manual config file
build
 - build --dry-run
add
 - set-remote
 - set-local
clean?

docbot needs a plugin for auto-setting the remote

- Add rez-config customization
 - source directory path
 - build directory path
 - sphinx default settings
 - sphinx extensions (like theme)

- need constants to be shared between rez_sphinx and rez_docbot
- need Qt example of the documentation

- Allow users to specify multiple potential publish keys
 - Add a configuration for a "try order". e.g. if X, use X, then try Y, etc.

- Add windows bin support

Make sure all :ref:`Sphinx` point to Sphinx's website
 - Same with rez-config https://github.com/nerdvegas/rez/wiki/Command-Line-Tools#rez-config
 - :ref:`Sphinx conf.py` - https://www.sphinx-doc.org/en/master/usage/configuration.html.
 - :ref:`sphinx-quickstart` - https://www.sphinx-doc.org/en/master/man/sphinx-quickstart.html
 - :ref:`rez_sphinx init`
 - :ref:`rez_sphinx build`
 - :ref:`rez help attribute` - https://github.com/nerdvegas/rez/wiki/Package-Definition-Guide#help
 - :ref:`intersphinx_mapping` - https://www.sphinx-doc.org/en/master/usage/extensions/intersphinx.html
 - :ref:`intersphinx` - https://www.sphinx-doc.org/en/master/usage/extensions/intersphinx.html
 - :ref:`sphinx.ext.autodoc` - https://www.sphinx-doc.org/en/master/usage/extensions/autodoc.html
 - :ref:`index.rst`
 - :ref:`help`
 - :ref:`rez_sphinx auto-help` - 
 - :ref:`rez-build`
 - :ref:`package help` - https://github.com/nerdvegas/rez/wiki/Package-Definition-Guide#help
 - :ref:`rez_sphinx tag` - documentation to where I explain the ..
 - :ref:`private_build_requires` - https://github.com/nerdvegas/rez/wiki/Package-Definition-Guide#private_build_requires
 - :ref:`package_preprocess_function`
 - :ref:`package.py`
 - :ref:`build_requires` - https://github.com/nerdvegas/rez/wiki/Package-Definition-Guide#build_requires
 - :ref:`requires` - https://github.com/nerdvegas/rez/wiki/Package-Definition-Guide#requires
 - :ref:`build_documentation_key` - The rez_sphinx key information
 - :ref:`sphinx-apidoc` - https://www.sphinx-doc.org/en/master/man/sphinx-apidoc.html
 - :ref:`toctree` - https://www.sphinx-doc.org/en/master/usage/restructuredtext/directives.html
 - :ref:`index.rst` - https://sphinx-tutorial.readthedocs.io/step-1/

- Add black_isort

- Make sure the schema parses user options correctly. It should fail when the user provides something wrong

- Add the ability to specify autoapi parameters

- Allow template headers so people can link back to company websites and what not
- Need an option for auto ``help`` attribute or baked in

readthedocs integration?

- Add a warning message that the user's preprocess function is not set

- Make main documentation in README.rst

- Make sure all :doc: and :ref: tags are written

- Go through BIG_IDEAS.md


test_existing_documentation_folder
test_existing_build_documentation_key
test_ignore_negated_packages (!foo-1 should not be auto-linked by rez-Sphinx)
test_ignore_ephemeral_packages (.foo-1 should not be auto-linked by rez-Sphinx)
