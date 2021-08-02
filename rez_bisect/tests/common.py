#!/usr/bin/env python

"""Basic file I/O, rez-agnostic functions for making unittests easier."""

import atexit
import functools
import os
import shutil
import stat
import tempfile


def make_directory():
    """str: Create a temporary directory and delete it later."""
    directory = tempfile.mkdtemp(suffix="_make_directory")
    atexit.register(functools.partial(shutil.rmtree, directory))

    return directory


def make_script(path, text):
    directory = os.path.dirname(path)

    if not os.path.isdir(directory):
        os.makedirs(directory)

    with open(path, "w") as handler:
        handler.write(text)

    os.chmod(path, os.stat(path).st_mode | stat.S_IEXEC)

    atexit.register(functools.partial(os.remove, path))


def make_temporary_script(commands):
    """Create a temporary shell script with `commands` and delete it later.

    Args:
        commands (str): Some shell script to run whenever this new file is called.

    Returns:
        str: The generated, temporary file.

    """
    with tempfile.NamedTemporaryFile(
        suffix="_script.sh", delete=False, mode="w"
    ) as handler:
        pass

    make_script(handler.name, commands)

    return handler.name
