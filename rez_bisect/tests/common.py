#!/usr/bin/env python

import atexit
import functools
import os
import shutil
import stat
import tempfile


def make_directory():
    directory = tempfile.mkdtemp(suffix="_make_directory")
    # atexit.register(functools.partial(shutil.rmtree, directory))

    return directory


def make_script(commands):
    with tempfile.NamedTemporaryFile(
        suffix="_script.sh", delete=False, mode="w"
    ) as handler:
        handler.writelines(commands)

    os.chmod(handler.name, os.stat(handler.name).st_mode | stat.S_IEXEC)

    return handler.name
