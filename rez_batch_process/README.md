``rez_batch_process`` has one purpose - to automate the process of changing Rez packages.

Rez is a great tool, but in a mature code-base of hundreds of Rez packages,
it's hard to make broad changes.

That's where ``rez_batch_process`` comes in.

``rez-batch-process`` is a command-line tool that finds Rez packages
and does an arbitrary command onto the Rez package. After the command
finishes, the change is applied as a new git branch and then submitted
as a pull request.

In other words, this tool doesn't to anything that can't be done
manually. But it does it all in a single execution.


# What can rez_batch_process do

Any shell command that you need to run on Rez packages, ``rez_batch_process`` can do.

# Example Use Cases

``rez_batch_process`` is very flexible with its built-in plug-in system.
And even without it, you can do many complex tasks automatically.
Here's some examples of things you could do with ``rez_batch_process``,
out of box.

- Add documentation to every Rez python package
- Bump cmake 2.8 to cmake 3 on every package that uses it
- Mark packages as deprecated
- Find every package that is affected by a new major version and refactor them with the latest change
- Add CI ``rez-test`` related checks onto packages
- Modify the structure of Rez packages


## How It Works

The basic steps that ``rez_batch_process`` are:

- Check every released package
- For each package family found, get the latest release
- Group every package by its published git repository (usually this data is written directly into the Rez package)
- Clone each repository once
- Do the command that the user has specified
- Create a new git branch, commit the changes, and submit a pull request for those changes
    - The pull request reviewers are auto-detected based on the Rez package's listed authors


# Features

``rez_batch_process`` comes with 2 commands. "check" and "fix".

"fix" is the "do it" command that actually modifies Rez packages.
"check" lets you preview the packages that would be changed by your command before it runs.
"check" is basically a dry-run of "fix".


# Example Command

Now for the bad news. ``rez_batch_process`` is great. But because its
syntax is a bit intense if you're not comfortable in command line.
This section breaks down the command line options so it becomes more
understandable.


## Basic Command

```sh
python -m rez_batch_process fix "touch test_file.txt" AS-1234 git-token
```

The above command adds a file called "test_file.txt" to every released
package. The only thing that you would need to change, if following
along, is ``git-token``. See this guide on
[how to create your own git token](https://help.github.com/en/github/authenticating-to-github/creating-a-personal-access-token-for-the-command-line).
Replace that option with your own personal access token so that git pull
requests will work with GitHub enterprise.


## Advanced Command

```sh
python -m rez_batch_process fix --keep-temporary-files --clone-directory /tmp/repository_clones/attempt_1 --packages rez_batch_process --base-url https://github-enterprise.com --search-packages-path `rez-config release_packages_path`:$REZ_PACKAGES_PATH "touch test_file.txt" AS-1234 git-token
```

```sh
python -m rez_batch_process fix --keep-temporary-files --search-packages-path `rez-config release_packages_path`:$REZ_PACKAGES_PATH "touch test_file.txt" AS-1234 git-token --temporary-director
y /tmp/foo/bar
```

Wow - the "advanced" command is huge! Let's break it down to make it more understandable.

TODO finish


# Extending rez-batch-process


# Current Caveats

``rez_batch_process`` only works with GitHub pull requests right now.
It could be extended to make pull requests in bitbucket. If that's the
case, add an issue here and it can be added.


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





- do more unittest. Variants class
-  make sure fix / reporting works with source packages that contain variants
 - and built packages

- does has_python_package account for source packages + variants? Because it needs to!
 - Also technically source packages need to be built in order to determine if they are a Python package


- Do CI stuff
- Do TODO notes

