- Add base unittests
- Check what sphinx.ext.githubpages is!!

init config
 - should also allow users to describe auto-added. e.g. API Documentation, User Documentation, Developer Documentation, etc. And their default messages
  - provide a default message ?
  - On build / on publish allow an auto-check to fail if the page has not been edited
  - Allow disabling of this functionality

- When converting "Tagged" Sphinx .rst files, add a unittest to make sure ":" is escapable. Since ":" is also the delimiter
- Need unittest so you cannot accidentally add the same file twice
- If the .. rez_sphinx comment (tag) is above a sphinx ref like .. _foo::, include that anchor in the text when it gets added to rez-help


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


- Consider replacing parts of preference.py with schema


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
- WRT API documentation
 - From {command line,config}
  - Allow to explicitly be auto
  - Allow to be as files on-disk
  - Do nothing
 - Make sure it can auto-detect reliably if API documentation needs to be explicit or auto-built
  - Could do this with a .gitignore and README.rst file or something


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
 - :ref:`private_build_requires` - https://github.com/nerdvegas/rez/wiki/Package-Definition-Guide#private_build_requires
 - :ref:`build_requires` - https://github.com/nerdvegas/rez/wiki/Package-Definition-Guide#build_requires
 - :ref:`requires` - https://github.com/nerdvegas/rez/wiki/Package-Definition-Guide#requires
 - :ref:`build_documentation_key` - The rez_sphinx key information
 - :ref:`sphinx-apidoc` - https://www.sphinx-doc.org/en/master/man/sphinx-apidoc.html
 - :ref:`toctree` - https://www.sphinx-doc.org/en/master/usage/restructuredtext/directives.html
 - :ref:`index.rst` - https://sphinx-tutorial.readthedocs.io/step-1/

- Add a way to convert to and from API types (full-auto and generate). I guess with ``rez_sphinx add``?

- Add black_isort

- Make sure the readthedocs.io theme can be added, via ``rez-config`` settings

- Add the ability to specify autoapi parameters

- Allow template headers so people can link back to company websites and what not
- Need an option for auto ``help`` attribute or baked in

readthedocs integration?

- Make main documentation in README.rst

- Make sure all :doc: and :ref: tags are written

- Go through BIG_IDEAS.md


test_existing_documentation_folder
test_existing_build_documentation_key
test_ignore_negated_packages (!foo-1 should not be auto-linked by rez-Sphinx)
test_ignore_ephemeral_packages (.foo-1 should not be auto-linked by rez-Sphinx)
