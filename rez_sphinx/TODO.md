- Get all tests to pass
- Follow the default header Python style (overlines) for all default pages
- Need unittest so you cannot accidentally add the same file twice to the same toctree
 - e.g. the default files must all have unique names, or error
- Make sure per-package config overriding is allowed

- Make sure the API tree looks pretty and isn't ugly

- Fix arrowed Sphinx conf.py references. They're broken
- Make sure all :doc: and :ref: tags are written

- On-build
 - Check if any pages are still defaults. And fail early
  - Add an option to disable this feature


- Add rez-config customization
 - source directory path
 - build directory path
 - sphinx default settings


- Check what sphinx.ext.githubpages is!!

init
build
 - build --dry-run
add
 - set-remote
 - set-local
clean?

docbot needs a plugin for auto-setting the remote

- need constants to be shared between rez_sphinx and rez_docbot
- need Qt example of the documentation

- Allow users to specify multiple potential publish keys
 - Add a configuration for a "try order". e.g. if X, use X, then try Y, etc.

- Add windows bin support

- Add black_isort

- Allow template headers so people can link back to company websites and what not

readthedocs integration?

- Add a warning message that the user's preprocess function is not set

- Make main documentation as README.rst

- Go through BIG_IDEAS.md


test_existing_documentation_folder
test_existing_build_documentation_key
test_ignore_negated_packages (!foo-1 should not be auto-linked by rez-Sphinx)
test_ignore_ephemeral_packages (.foo-1 should not be auto-linked by rez-Sphinx)
