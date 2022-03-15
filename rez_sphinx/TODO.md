- Get all tests to pass
- Make sure source file finding works, even with symlinked, installed Rez packages
- Make sure the "auto-help ref role tagging" feature actually works. I'm almost
  100% we need the header label, NOT the ref label.
- Need unittest so you cannot accidentally add the same file twice to the same toctree
- Make sure per-package config overriding is allowed

- On-build
 - Check if any pages are still defaults. And fail early
  - Add an option to disable this feature


- config subparser
 - print a default configuration for the user
  - as yaml
  - as python?


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

init
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

- Add black_isort

- Make sure the schema parses user options correctly. It should fail when the user provides something wrong

- Allow template headers so people can link back to company websites and what not

readthedocs integration?

- Add a warning message that the user's preprocess function is not set

- Make main documentation in README.rst

- Make sure all :doc: and :ref: tags are written

- Go through BIG_IDEAS.md


test_existing_documentation_folder
test_existing_build_documentation_key
test_ignore_negated_packages (!foo-1 should not be auto-linked by rez-Sphinx)
test_ignore_ephemeral_packages (.foo-1 should not be auto-linked by rez-Sphinx)
