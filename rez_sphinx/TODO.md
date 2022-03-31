- Make the build_documentation fully optional

- Is it possible to use a pre-release hook in order to edit the help attribute, instead of preprocess?
 - Because if so that'd be way faster to handle

- Replace NoneType with None
- make sure all get_nearest_rez_package calls check for None!
 - rez_sphinx
 - rez_docbot
- :ref:`rez_sphinx` is auto-tagging to "User Documentation". It makes
  reading documentation pretty difficult. Change :ref:`rez_sphinx` as needed to
  literally read as "rez_sphinx", instead
  - Also fix rez_docbot. It's weird that I have to keep renaming it
- Add check so API documentation isn't added again if the user renames it
- Do a pass through existing TODO notes in rez_sphinx
- Version publishing
  - Add option to allow overwriting a version folder if the user is publishing
	a patch to the same major.minor version. And allow toggle to forbid it.
	- Maybe make this the default?

- Consider preventing preprocess from running when calling DeveloperPackage.from_path / get_nearest_rez_package

- If you just use ``rez_sphinx_help`` and omit the optional label after ":", the
top-level header of that file is used as a label, instead.
 - Make sure this works
 - If there's no valid header found, use the current file name, instead

- Check out why the "Skipping preprocessor because" message happens so much during rez_sphinx publish run

- Add a pre-install plugin which adds the destination URL as needed
  - This needs to work even if the documentation repository hasn't already been created
  - Or maybe it's fine to create the repository right then and there? Not sure
- Add a Rez plugin for post release publishing

- Every command that accepts a directory should have a test for if it isn't found. Probably.
- Make sure commands run without subcommands or --help give the right output.
  They shouldn't just AttributeError. e.g. `rez_sphinx view` raises
  AttributeError
- Should make some tests for invalid quickstart / build / API arguments

- Add pylint configuration to match with black (line length 88)
- Do all general TODO notes
- Do all NotImplementedError, where applicable

- Check why rez_sphinx config show sphinx-apidoc.arguments fails
- Check why rez_sphinx config show --list-all oes not show "intersphinx_settings" or its children
- silence build commands

- Add unittests for the plugin / preprocess hooks
 - If it needs to be dependency-less, make a unittest that enforces this

- Make sure the preprocess function works as a general, standalone thing

- Need to ensure docbot's logger is set properly when used as a bolt-in for rez_sphinx


## Document current work

- Do all TODO notes within the documentation/source folder
- Consider adding refs to "documentation source root" so people know what I'm talking about
- Consider adding refs to "documentation build root" so people know what I'm talking about
- Add option to prefer hand-written API documentation, if provided

- If `help`_ rez_sphinx objects.inv points to a non-URL, check if it's
  absolute. If relative, absolute-ize it based onthe package directory and then
  use that
  - If they make a mistake and point directly to objects.inv, crop it to the real directory / URL path


## Make tools more robust
- Make sure rez_sphinx only adds its bootstrap once
- Follow the default header Python style (overlines) for all default pages
- Need unittest so you cannot accidentally add the same file twice to the same toctree
 - e.g. the default files must all have unique names, or error
- Make sure per-package config overriding is allowed
 - Make sure config settings can be overwritten at the package level, generally
 - When the user runs ``rez_sphinx config list-overrides`` in a directory
   within a Rez package, grab the package's config overrides, too
   - Make sure ``rez_sphinx config check`` does this too
 
## apidoc fixes
- apidoc stuff
 - make sure the tree looks nice
  - names should be sparse
  - no duplicates
  - API documentation modules
   - Make sure the functions are just the short names. No long names

- Bootstrap suffix
 - Allow the user to append extra lines to the bootstrapper
- Allow arguments to the rez_sphinx build
 - from CLI
 - from config

- Make sure auto-linking cannot fail if the Rez package.py has undefined / syntax error in its contents


- And an option to specify the destination URL for docbot directly on the package.py
- When interlinking, check for Internet
 - Add an option to not check for it
 - post release, maybe add an option to check that each path in rez-help points to something. Fail if happens

- Make sure to set `latex_documents` in `conf.py`
 - man_pages
 - https://github.com/nerdvegas/rez/blob/master/docs/conf.py
 - texinfo_documents
 - https://www.sphinx-doc.org/en/master/usage/configuration.html#confval-latex_documents
  - make sure to set authors correctly

- Look into if GitHub actions might be a better way of getting documentation to users
 - Look at nerdvegas's code as a blueprint

- Make sure custom default_files
 - Append to the toctree as expected
 - Are checked for, properly


- Add check to reject non-package.py Rez files (error on package.yaml / .yml / .txt)
- Make sure ``build`` fails if no ``init`` was ran.

- Allow `.. rez_sphinx_help` as a valid key, instead of forcing it to be 2 lines long
- Change html_theme to be a choice list, with fallbacks
- Adding environment variables for building rez_sphinx

- Add black_isort

- Needs to be able to run / exit early when there's no Python files

- Add option to prevent API documentation from being overwritten

- Make sure all :doc: and :ref: tags are written

- On-build
 - Check if any pages are still defaults. And fail early
  - Add an option to disable this feature


- Make sure the CLI feels good
 - not specifying a command should always show the help menu

- Consider removing build.rxt files from the repository before merging

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

- Allow template headers so people can link back to company websites and what not

readthedocs integration?

- Add a warning message that the user's preprocess function is not set

- Make main documentation as README.rst

- Go through BIG_IDEAS.md

test_existing_documentation_folder
test_existing_build_documentation_key
test_ignore_negated_packages (!foo-1 should not be auto-linked by rez-Sphinx)
test_ignore_ephemeral_packages (.foo-1 should not be auto-linked by rez-Sphinx)

- Check unittest for printed errors after everything is working, everywhere
