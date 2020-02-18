``rez_batch_process`` has one purpose - to automate the process of changing Rez packages.

Rez is a great tool, but in a mature code-base of hundreds of Rez packages,
it's hard to make broad changes to many Rez packages at once.

That's where ``rez_batch_process`` comes in.

``rez-batch-process`` is a command-line tool that finds Rez packages
and runs an arbitrary command on the Rez package. After the command
finishes, the change is applied as a new git branch and then submitted
as a pull request.

In other words, this tool doesn't to anything that can't be done
manually. But it does it all in a single execution.


# What can rez_batch_process do

Any shell command that you need to run on Rez packages, ``rez_batch_process`` can do.


# Example Use Cases

``rez_batch_process`` is very flexible with its built-in plug-in system.
And even without using it, you can do many complex tasks automatically.
Here's some examples of things you could do with ``rez_batch_process``,
out of box.

- Bump cmake 2.8 to cmake 3 on every package that uses it
- Move imports and deprecate Rez packages
- Add CI ``rez-test`` related checks onto packages
- Add documentation to every Rez python package
- Modify the structure of Rez packages

As long as you've got a shell command that runs from a Rez package root,
any of these tasks are possible without extending ``rez_batch_process``.

For examples of ``rez_batch_process`` in-use, see
[``rez_batch_plugins``](../rez_batch_plugins).


# Example Commands

1. Check which packages would be affected by a given command

```sh
python -m rez_batch_process check {command-name} {command-arguments}
```

2. Run the command

```sh
python -m rez_batch_process run {command-name} {command-arguments}
```

3. Create a JSON cache of GitHub users which can be used for the
   "--cached-users" flag for other commands.

```sh
python -m rez_batch_process make-git-users
```


# How It Works

The basic steps that ``rez_batch_process`` are:

- Check every released package
- For each package family found, get the latest release
- Group every package by its published git repository (usually this data is written directly into the Rez package)
- Clone each repository once
- Run ``cd`` into each Rez package in the repository
- Do the command that the user has specified
- Create a new git branch, commit the changes, and submit a pull request for those changes
    - The pull request reviewers are auto-detected based on the Rez package's listed authors


# Features

``rez_batch_process`` comes with 2 commands. "report" and "run".

"run" is the "do it" command that actually modifies Rez packages and makes pull requests.
"report" lets you preview the packages that would be changed by your command before it runs.
"report" is basically a dry-run of "run".


# Example Command

Now for the bad news. ``rez_batch_process`` is great. But its syntax is
a bit intense. This section breaks down the command line options so it
becomes more understandable.


## Basic Command

```sh
python -m rez_batch_process run "touch test_file.txt" AS-1234 git-token
```

The above command adds a file called "test_file.txt" to every released
package. The only thing that you would need to change, if following
along, is ``git-token``. See this guide on
[how to create your own git token](https://help.github.com/en/github/authenticating-to-github/creating-a-personal-access-token-for-the-command-line).
Replace the "git-token" text with your own personal access token so that
git pull requests will work with GitHub / GitHub enterprise.


## Advanced Command

Here's a command that adds "test_file.txt" to a Rez package called
"rez_batch_process", located in some GitHub Enterprise website.

TODO implement this
```sh
python -m rez_batch_process run --keep-temporary-files --clone-directory /tmp/repository_clones/attempt_1 --packages rez_batch_process --search-packages-path `rez-config release_packages_path`:$REZ_PACKAGES_PATH "touch test_file.txt" --temporary-directory /tmp/foo/bar shell AS-1234 git-token --base-url https://github-enterprise.com
```

This is an example of most parameters that ``rez_batch_process`` comes with by default.

Wow - the "advanced" command is huge! Let's break it down to make it more understandable.

TODO finish


# Extending rez-batch-process

TODO explain the plugin stuff


# Current Caveats

``rez_batch_process`` only works with GitHub pull requests right now.
It could be extended to make pull requests in bitbucket. If that's the
case, add an issue here and it can be added.

- do more unittest. Variants class
-  make sure run / reporting works with source packages that contain variants
 - and built packages


TODO make sure that pull requests are only created if anything was actually changed
- Make unittest for filtering / skipping packages. Make sure that stuff works
