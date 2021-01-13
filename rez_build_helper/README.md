- Add a clean-on-exit context
- Make sure the EGG has as much data as possible
- Make sure python version is not forced

A basic wrapper around Rez's
[build_command](https://github.com/nerdvegas/rez/wiki/Package-Definition-Guide#build_command).

It exists basically to make Rez Python packages (or other types of packages, if needed)

- buildable with a single line
- no extra files
- support symlinking


## How To Run

Add this to your Rez package.py file.

```python
private_build_requires = ["rez_build_helper-1+<2"]

build_command = "python -m rez_build_helper --items bin python"
```

In this example, we're saying "Use rez_build_helper to install the "bin"
and "python" folders". Each path given must be relative to the Rez
package's root directory. The paths can be files or folders.


## Symlink Support

``rez_build_helper`` allows you to build with symlinks from a single flag, ``--symlink``.

Here's an example command:

```sh
rez-build -ci -- --symlink
```

``-ci`` is short-hand for ``--clean --install`` (and are standard
rez-build arguments). If you want to pass any arguments directly to
``rez_build_helper``, they must be separated with a `` -- ``.

In my own ``~/.profile``, there lives this alias.

```sh
alias rb="rez-build --clean --install -- --symlink"
```

With this, building anything with symlinks is just an ``rb`` away.


## .egg for Python packages

If you want to convert a folder into a .egg file, just replace
``--items`` with ``--egg``. When built, the .egg file will be named
after whatever the folder is called.


## Building Houdini HDAs
Use ``--hdas`` to note any folders which contain Houdini HDAs. The
folder structure should look like this:

```
- some_folder_name (usually, just "hdas")
    - some_hda_name
	    - houdini.hdalibrary
		- other
		- files
```

And then rez_build_helper looks like this:

```python
build_command = "python -m rez_build_helper --hdas hda"
```

The key points are, ``--hdas`` expects folder names. And in each folder,
there should inner folders, containing Houdini HDAs. Each HDA folder
should have a "houdini.hdalibrary" file directly inside of it.


## Calling rez_build_helper Manually

If you want to take advantage of ``rez_build_helper``'s functions, you can write your own build script.

```python
private_build_requires = ["rez_build_helper-1+<2"]

build_command = "python {root}/rezbuild.py {install}"
```

And then in the ``rezbuild.py`` file.

```python
#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The main module which installs the package onto the user's system."""

import os
import sys

from rez_build_helper import filer


def build(source_path, build_path, install_path, targets):
	# `build_path` here doesn't do anything. But can be used if you need it for anything
    filer.build(source_path, install_path, targets)

if __name__ == "__main__":
    build(
        source_path=os.environ["REZ_BUILD_SOURCE_PATH"],
        build_path=os.environ["REZ_BUILD_PATH"],
        install_path=os.environ["REZ_BUILD_INSTALL_PATH"],
        targets=sys.argv[1:],

```
