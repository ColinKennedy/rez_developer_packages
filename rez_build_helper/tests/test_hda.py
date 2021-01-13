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
from rez import resolved_context
from six.moves import mock

from .common import common, creator, finder


class Hda(common.Common):
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
            creator.build(package, destination, quiet=True, packages_path=self._packages_path)

        install_location = os.path.join(destination, "some_package", "1.0.0")
        self.assertTrue(os.path.isfile(os.path.join(install_location, file_name)))
        self.assertTrue(os.path.isdir(os.path.join(install_location, "hda")))

    def test_invalid(self):
        raise ValueError()

    def test_symlink(self):
        """Build symlinks, instead of collapsing the OTL."""
        directory = tempfile.mkdtemp(
            prefix="rez_build_helper_Hda_test_symlink_source_directory_",
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

                    build_command = "python -m rez_build_helper --hdas hda -- --symlink"
                    """
                )
            )

        package = finder.get_nearest_rez_package(directory)
        destination = tempfile.mkdtemp(prefix="rez_build_helper_Hda_test_symlink_destination_")
        atexit.register(functools.partial(shutil.rmtree, destination))

        file_name = "hotl.txt"

        with _patch_hotl(file_name):
            creator.build(package, destination, quiet=True, packages_path=self._packages_path)

        install_location = os.path.join(destination, "some_package", "1.0.0")
        self.assertFalse(os.path.isfile(os.path.join(install_location, file_name)))
        hda = os.path.join(install_location, "hda")
        files = os.listdir(hda)

        for item in files:
            path = os.path.join(hda, item)

            self.assertTrue(os.path.islink(path))

        self.assertTrue(files)


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

    # def _execute(self, *args, **kwargs):
    #     kwargs["env"] = {"PATH": "BLAH_"}
    #
    #     return self.execute_shell(*args, **kwargs)
    #
    # with wrapping.keep_os_environment():
    #     os.environ["PATH"] = new_path
    #
    #     with mock.patch(
    #         "rez.resolved_context.ResolvedContext.execute_shell",
    #         new=_execute,
    #     ):
    #         yield

    def _execute(self, *args, **kwargs):
        kwargs["env"] = {"PATH": "BLAH_"}

        return self.execute_shell(*args, **kwargs)

    def _wrap(function):
        def wrapper(*args, **kwargs):
            kwargs["parent_environ"] = {"PATH": "asdf"}

            return function(*args, **kwargs)

        return wrapper

    with wrapping.keep_os_environment():
        os.environ["PATH"] = new_path
        original = resolved_context.ResolvedContext.execute_shell

        try:
            resolved_context.ResolvedContext.execute_shell = _wrap(resolved_context.ResolvedContext.execute_shell)

            yield
        finally:
            resolved_context.ResolvedContext.execute_shell = original


# def copytree(source, destination, symlinks=False, ignore=None):
#     """Copy `source` into `destination`.
#
#     Why is this not just default behavior. Guido, explain yourself!
#
#     Reference:
#         https://stackoverflow.com/a/12514470/3626104
#
#     Args:
#         source (str):
#             The folder to copy from.
#         destination (str):
#             The folder to copy into.
#         symlinks (bool, optional):
#             If True, copy through symlinks. If False, copy just the
#             symlink. Default is False.
#         ignore (set[str], optional):
#             The names of the files/folders to ignore during copy.
#
#     """
#     for item in os.listdir(source):
#         source_ = os.path.join(source, item)
#         destination_ = os.path.join(destination, item)
#
#         if os.path.isdir(source_):
#             shutil.copytree(source_, destination_, symlinks, ignore)
#         else:
#             shutil.copy2(source_, destination_)
