- do more unittest. Variants class
-  make sure fix / reporting works with source packages that contain variants
 - and built packages

- does has_python_package account for source packages + variants? Because it needs to!
 - Also technically source packages need to be built in order to determine if they are a Python package


- Do CI stuff
- Do TODO notes

``rez-documentation-search`` is a command-line tool that finds Rez
packages that are missing Sphinx documentation. It also has the option
to auto-add documentation to those packages.


## How It Works

The tool can be summarized as follows

- Get the latest version of every Rez package family
- If that Rez package implements a Python package, it is a "candidate for documentation"
- If the package doesn't have documentation, report it to the user

When the user choose "fix" instead of "check", the program will not
report the packages to the user. Instead, it will

- Clone the Rez package's repository, if needed
- Make a new branch for the package in the repository that needs to be changed
- Add the documentation
- Commit everything and push the branch to the remote repository
- Create a PR to merge back to the default branch (or develop branch, if it exists)
- If there are more packages in the repository that also need
documentation, repeat branches + PRs etc until there are no more
packages.

It basically automates what is otherwise a tedious, manual process.


## Example Command

### Basic Command

```sh
python -m rez_documentation_search fix "touch test_file.txt" AS-1234 4af47dcab34dd15aebf07239ab8e78c8e68689c6
```

### Advanced Command

```sh
python -m rez_documentation_search fix --keep-temporary-files --clone-directory /tmp/repository_clones/attempt_1 --packages rez_documentation_search --base-url https://github-enterprise.com --search-packages-path `rez-config release_packages_path`:$REZ_PACKAGES_PATH "touch test_file.txt" AS-1234 4af47dcab34dd15aebf07239ab8e78c8e68689c6
```

```sh
python -m rez_documentation_search fix --keep-temporary-files --search-packages-path `rez-config release_packages_path`:$REZ_PACKAGES_PATH "touch test_file.txt" AS-1234 4af47dcab34dd15aebf07239ab8e78c8e68689c6 --temporary-director
y /tmp/foo/bar
```

Wow - the "advanced" command is huge! Let's break it down to make it more understandable.

TODO finish


## Extending rez-documentation-search

TODO explain the plugin stuff

TODO - Check all rez package and their unittests / CI / coverage

 - python_compatibility
 - rez_documentation_check
 - rez_documentation_search
 - rez_utilities

TODO
- do needs "intersphinx" finder
 - traverse all possible Rez packages
  - Check if the Rez package has a conf.py
   - Run the "missing intersphinx" check
   - if anything missing comes up, do
    - group by repository
	- clone everything
	- make the change as individual rez packages
	- create a PR for each change
	 - find a way to auto-add reviewers. No idea how to do this though ...

   - Make the logic that determines this into a separate function / module so that it can be overwritten,if needed
   - run the paths through a process (arbitrary user process / function)

- Add wrapper code that can auto-add intersphinx to fixes to Rez packages and create a PR
