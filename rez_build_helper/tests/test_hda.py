#!/usr/bin/env python
# -*- coding: utf-8 -*-

import atexit
import contextlib
import functools
import os
import shutil
import stat
import tempfile
import textwrap
import unittest

from python_compatibility import wrapping

from .common import common, creator, finder


class Hda(unittest.TestCase):
    """All tests related to building Houdini HDAs."""

    def test_which(self):
        """Make sure the we get the hotl correctly."""
        raise ValueError()

    def test_collapse(self):
        directory = tempfile.mkdtemp(
            prefix="rez_build_helper_Hda_test_collapse_source_directory_",
        )
        atexit.register(functools.partial(shutil.rmtree, directory))

        common.make_files(
            {
                "hda": {
                    "blah": {
                        "houdini.hdalibrary": None,
                    }
                },
            },
            directory,
        )

        with open(os.path.join(directory, "package.py"), "w") as handler:
            handler.write(
                textwrap.dedent(
                    """\
                    name = "some_package"

                    version = "1.0.0"

                    private_build_requires = ["rez_build_helper"]

                    build_command = "python -m rez_build_helper --hdas hda"
                    """
                )
            )

        package = finder.get_nearest_rez_package(directory)
        destination = tempfile.mkdtemp(prefix="rez_build_helper_Hda_test_collapse_destination_")
        atexit.register(functools.partial(shutil.rmtree, destination))

        file_name = "hotl.txt"

        with _patch_hotl(file_name):
            creator.build(package, destination)

        install_location = os.path.join(destination, "some_package", "1.0.0")
        self.assertTrue(os.path.isfile(os.path.join(install_location, file_name)))
        self.assertTrue(os.path.isdir(os.path.join(install_location, "hda")))

    def test_invalid(self):
        raise ValueError()

    def test_symlink(self):
        raise ValueError()


@contextlib.contextmanager
def _patch_hotl(fake_path_name):
    path = os.getenv("PATH", "")
    prefix = tempfile.mkdtemp(suffix="_patch_hotl")
    atexit.register(functools.partial(shutil.rmtree, prefix))
    hotl = os.path.join(prefix, "hotl")

    template = textwrap.dedent(
        """\
        python -c 'open("{fake_path_name}", "a").close()'
        """
    )

    with open(hotl, "w") as handler:
        handler.write(template.format(fake_path_name=fake_path_name))

    # Make `hotl` executable
    stats = os.stat(hotl)
    os.chmod(hotl, stats.st_mode | stat.S_IEXEC)

    new_path = "{prefix}{os.pathsep}{path}".format(
        prefix=prefix,
        os=os,
        path=path,
    )

    with wrapping.keep_os_environment():
        os.environ["PATH"] = new_path

        yield
