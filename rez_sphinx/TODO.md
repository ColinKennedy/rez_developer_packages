- Add base unittests


- Auto-discover python code based on the appends to PYTHONPATH

init
 ---add-remote
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
Same with rez-config https://github.com/nerdvegas/rez/wiki/Command-Line-Tools#rez-config

readthedocs integration?

- Make main documentation in README.rst

- Make sure all :doc: and :ref: tags are written

- Go through BIG_IDEAS.md


test_existing_documentation_folder
test_existing_build_documentation_key
test_ignore_negated_packages (!foo-1 should not be auto-linked by rez-Sphinx)
test_ignore_ephemeral_packages (.foo-1 should not be auto-linked by rez-Sphinx)
