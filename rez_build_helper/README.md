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