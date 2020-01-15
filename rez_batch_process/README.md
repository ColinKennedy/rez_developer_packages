``rez_batch_process`` has one purpose - to automate the process of changing Rez packages.

Rez is a great tool, but in a mature code-base of hundreds of Rez packages,
it's hard to make broad changes.

That's where ``rez_batch_process`` comes in.


# What can rez_batch_process do

Any shell command that you need to run on Rez packages, ``rez_batch_process`` can do.

Here's some quick example use-cases

- Add documentation to every Rez python package
- Bump cmake 2.8 to cmake 3 on every package that uses it
- Mark packages as deprecated
- Change the requirements of Rez packages, making it easy and painless to increment a major version
- Add CI ``rez-test`` related checks onto packages
- Modify the structure of Rez packages
- Prank your friends :)


``rez-batch-process`` is a command-line tool that finds Rez
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
python -m rez_batch_process fix "touch test_file.txt" AS-1234 git-token
```

### Advanced Command

```sh
python -m rez_batch_process fix --keep-temporary-files --clone-directory /tmp/repository_clones/attempt_1 --packages rez_batch_process --base-url https://github-enterprise.com --search-packages-path `rez-config release_packages_path`:$REZ_PACKAGES_PATH "touch test_file.txt" AS-1234 git-token
```

```sh
python -m rez_batch_process fix --keep-temporary-files --search-packages-path `rez-config release_packages_path`:$REZ_PACKAGES_PATH "touch test_file.txt" AS-1234 git-token --temporary-director
y /tmp/foo/bar
```

Wow - the "advanced" command is huge! Let's break it down to make it more understandable.

TODO finish


## Extending rez-batch-process

TODO explain the plugin stuff

TODO - Check all rez package and their unittests / CI / coverage

 - python_compatibility
 - rez_documentation_check
 - rez_batch_process
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
