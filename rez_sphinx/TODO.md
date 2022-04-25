- do TODO notes / Todo / NotImplementedError

- when building documentation to installed packages locally, `{root}/` needs to
  be replaced with "" so that the paths are relative and `rez-help` can still work!


- post release support
 - check if it can use relative paths without appending to the main PYTHONPATH
  - If so, abuse that
 - if it can't, make a context of "current package + rez_sphinx"
  - error early if the user is missing publish details
  - ensure ephemerals are passed in
  - call `rez_sphinx publish run`
   - handle output
    - error if returncode is bad - print stderr
    - print stdout


- Add release hook post release support!
 - unittest it

- Need to ensure docbot's logger is set properly when used as a bolt-in for rez_sphinx
- If people try to define objects.inv `help` manually and make a mistake and
  point directly to objects.inv instead of the folder, crop it to the real
  directory / URL path
- Do rez_docbot preferences unittests


# Batch processing TODO
 - make sure the batch processing tutorial works
	- name
	- version
	- push_url (if installed)

- Consider adding refs to "documentation source root" so people know what I'm talking about
- Consider adding refs to "documentation build root" so people know what I'm talking about

- Make sure help doesn't replace any relative paths which actually exist in the package
 - Nor absolute paths
 - Allow manual paths to be replaced but only if they define a {root}

- Make the build_documentation fully optional
- Possibly move rezplugins to its own folder, outside of the Python folder


- silence build commands
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

- Go through BIG_IDEAS.md


## High Level TODO
### Tutorials
- need Qt example of the documentation - showing docs in a menu
- Batch applying the documentation
