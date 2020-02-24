``rez_batch_process`` has one purpose - to automate the process of changing Rez packages.

Rez is a great tool, but in a mature code-base of hundreds of Rez packages,
it's hard to make broad changes to many Rez packages at once.

That's where ``rez_batch_process`` comes in.

``rez_batch_process`` is a command-line tool that finds Rez packages
and runs an arbitrary command on the Rez package. After the command
finishes, the change is applied as a new git branch and then submitted
as a pull request.

In other words, this tool doesn't to anything that can't be done
manually. But it does it all in a single execution.


# What can rez_batch_process do

Any shell command that you need to run on Rez packages, ``rez_batch_process`` can do.


# Example Commands

1. Check which packages would be affected by a given command

```sh
python -m rez_batch_process report shell {command-name} {command-arguments}
```

2. Run the command

```sh
python -m rez_batch_process run shell {command-name} {command-arguments}
```

3. Create a JSON cache of GitHub users which can be used for the
   "--cached-users" flag for other commands. (Including --cached-users
   makes the command run much faster).

```sh
python -m rez_batch_process make-git-users git-token /tmp/output.json
```


``rez_batch_process`` comes with one command, "shell", by default.
It lets you run shell commands on all of your Rez packages. But
``rez_batch_process`` lets you customize both the command that you want
to run and the packages that the command will be run on, with a little
bit of set-up.


```sh
python -m rez_batch_process run shell "touch test_file.txt" AS-1234 git-token
```

The above command adds a file called "test_file.txt" to every released
package. The only thing that you would need to change, if following
along, is ``git-token``. See this guide on
[how to create your own git token](https://help.github.com/en/github/authenticating-to-github/creating-a-personal-access-token-for-the-command-line).
Replace the "git-token" text with your own personal access token so that
git pull requests will work with GitHub / GitHub enterprise.


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


## Advanced Command

Here's probably the most complex command you'd use with
``rez_batch_process``. Almost every argument is optional but, when
included, makes your command more robust or execute faster.

In this example, we're going to add "test_file.txt" to a Rez package
called "rez_batch_process", located in some GitHub Enterprise
website (not the standard GitHub site, which is the default for
``rez_batch_process``).

```sh
python -m rez_batch_process run shell --keep-temporary-files --clone-directory /tmp/repository_clones/attempt_1 --packages rez_batch_process --search-packages-path `rez-config release_packages_path`:$REZ_PACKAGES_PATH "touch test_file.txt" --temporary-directory /tmp/foo/bar shell AS-1234 git-token --base-url https://github-enterprise.com --cached-users /tmp/some_users.json
```

Wow - the "advanced" command is huge! Let's break it down to make it more understandable.

``rez_batch_process run`` options:

```
--clone-directory: In order to modify and submit PRs, we clone git repositories. This directory will be used for every repository that's cloned. If you re-run your command, these repositories will be re-used.
--keep-temporary-files: Don't delete the cloned git repositories
--packages: The "shell" command modifies every Rez package, by default. This explicit list will make sure it only modifies just those packages.
--search-packages-path: The paths used to search for anything in --packages
--
```

"shell" options

```
AS-1234: This string can be whatever you want it to be. It'll be the prefix of submitted PRs
git-token: A GitHub access token. See [GitHub Access Tokens](GitHub-Access-Tokens) for details
--base-url: If your GitHub address isn't the standard github.com URL, add it here
--cached-users: A JSON generated by the "make-git-users" command. If this isn't provided
    rez_batch_process has to query users every time to find reviewers to
    add to the PRs that it generates. That query in GitHub's REST API is
    pretty slow so always add users, whenever you can.
```

You'll see that most of the flags are for optimization. But they're
worth taking the extra time because in a big edit, it'll save you a lot
of headaches.


TODO deprecate the need for --base-url. IMO the found remote should auto-parse the enterprise URL
 - This'll also need to work for all git syntaxes, like SSH-style


# Extending rez-batch-process

You can use the "shell" command for common operations. But if you want ``rez_batch_process``
to work directly with Python, it requires a bit of extra set-up. Usually
you won't need to do this but if you need extra control over how packages
are discovered, for example, plugins are how ``rez_batch_process`` lets you do it.

There's some examples in [``rez_batch_plugins``](../rez_batch_plugins)
to show how to implement plugins.

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
