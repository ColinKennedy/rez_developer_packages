- Consider adding refs to "documentation source root" so people know what I'm talking about
- Consider adding refs to "documentation build root" so people know what I'm talking about

- Add option to prefer hand-written API documentation, if provided



- Do rez_docbot preferences unittests
- Add check so API documentation isn't added again if the user renames it
- Need to ensure docbot's logger is set properly when used as a bolt-in for rez_sphinx

- If people try to define objects.inv `help` manually and make a mistake and point directly to objects.inv instead of the folder, crop it to the real directory / URL path

- Make sure help doesn't replace any relative paths which actually exist in the package
 - Nor absolute paths
 - Allow manual paths to be replaced but only if they define a {root}

- When auto-publishing, make sure to try publishing through each publisher.
  Don't just publish the first one found

- Do a pass through existing TODO notes in rez_sphinx

- Make the build_documentation fully optional
- Possibly move rezplugins to its own folder, outside of the Python folder


- silence build commands

- If you just use ``rez_sphinx_help`` and omit the optional label after ":", the
top-level header of that file is used as a label, instead.
 - Make sure this works
 - If there's no valid header found, use the current file name, instead

- Check out why the "Skipping preprocessor because" message happens so much during rez_sphinx publish run

- Add pylint configuration to match with black (line length 88)
- Do all general TODO notes
- Do all NotImplementedError, where applicable

- Add unittests for the plugin / preprocess hooks
 - If it needs to be dependency-less, make a unittest that enforces this

- Make sure auto-linking doesn't fail midway if the Rez package.py has undefined / syntax error in its contents

- Look into if GitHub actions might be a better way of getting documentation to users
 - Look at nerdvegas's code as a blueprint

- Allow `.. rez_sphinx_help` as a valid key, instead of forcing it to be 2 lines long
- Change html_theme to be a choice list, with fallbacks
- Adding environment variables for building rez_sphinx

- Add black_isort


- On-build
 - Check if any pages are still defaults. And fail early
  - Add an option to disable this feature

- Consider removing build.rxt files from the repository before merging

- Check what sphinx.ext.githubpages is!!

- need constants to be shared between rez_sphinx and rez_docbot

- Allow users to specify multiple potential publish keys
 - Add a configuration for a "try order". e.g. if X, use X, then try Y, etc.

- Add windows bin support

- Allow template headers so people can link back to company websites and what not

readthedocs integration?

- Add a warning message that the user's preprocess function is not set

- Make main documentation as README.rst

- Go through BIG_IDEAS.md


## Clean-up Checks
- Make sure all :doc: and :ref: tags are written
- Check for unfinished TODO / NotImplementedHere in source code and in documentation


## High Level TODO
### Tutorials
- need Qt example of the documentation - showing docs in a menu
- Batch applying the documentation
