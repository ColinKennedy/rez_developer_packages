#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""All tests related to building, collapsing, and symlinking HDAs."""

import atexit
import contextlib
import functools
import os
import shutil
import stat
import tempfile
import textwrap

from python_compatibility import wrapping
from rez import resolved_context
from rez_build_helper import filer

from .common import common, creator, finder


class Hda(common.Common):
    """All tests related to building Houdini HDAs."""

    def test_which(self):
        """Make sure the we get the hotl correctly.

        This path is only used for testing. In production, this should
        point to a Houdini ``hotl`` binary file.

        """
        self.assertEqual(
            os.path.join(os.environ["REZ_REZ_BUILD_HELPER_ROOT"], "fake_bin", "hotl"),
            filer._get_hotl_executable(),  # pylint: disable=protected-access
        )

    def test_collapse(self):
        """Collapse a HDA VCS folder into a single HDA file.

        This test doesn't actually do the collapse. But it tests the
        logic which would do it.

        """
        directory = tempfile.mkdtemp(
            prefix="rez_build_helper_Hda_test_collapse_source_directory_",
        )
        atexit.register(functools.partial(shutil.rmtree, directory))

        common.make_files(
            {"hda": {"blah": {"houdini.hdalibrary": None,}},}, directory,
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
        destination = tempfile.mkdtemp(
            prefix="rez_build_helper_Hda_test_collapse_destination_"
        )
        atexit.register(functools.partial(shutil.rmtree, destination))

        file_name = "hotl.txt"

        with _patch_hotl(file_name):
            creator.build(
                package, destination, quiet=False, packages_path=self._packages_path
            )

        install_location = os.path.join(destination, "some_package", "1.0.0")
        self.assertTrue(
            os.path.isfile(os.path.join(install_location, "hda", "blah", file_name))
        )
        self.assertTrue(os.path.isdir(os.path.join(install_location, "hda", "blah")))
        self.assertFalse(os.path.islink(os.path.join(install_location, "hda", "blah")))

    def test_symlink(self):
        """Build symlinks, instead of collapsing the OTL."""
        directory = tempfile.mkdtemp(
            prefix="rez_build_helper_Hda_test_symlink_source_directory_",
        )
        atexit.register(functools.partial(shutil.rmtree, directory))

        common.make_files(
            {"hda": {"blah": {"houdini.hdalibrary": None,}},}, directory,
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
        destination = tempfile.mkdtemp(
            prefix="rez_build_helper_Hda_test_symlink_destination_"
        )
        atexit.register(functools.partial(shutil.rmtree, destination))

        file_name = "hotl.txt"

        with _patch_hotl(file_name):
            creator.build(
                package, destination, quiet=True, packages_path=self._packages_path
            )

        install_location = os.path.join(destination, "some_package", "1.0.0")
        self.assertFalse(os.path.isfile(os.path.join(install_location, file_name)))
        hda = os.path.join(install_location, "hda")
        files = os.listdir(hda)

        for item in files:
            path = os.path.join(hda, item)

            self.assertTrue(os.path.islink(path))

        self.assertEqual(["blah"], files)


# TODO : Check if this can be removed.
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

    new_path = "{prefix}{os.pathsep}{path}".format(prefix=prefix, os=os, path=path,)

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
            resolved_context.ResolvedContext.execute_shell = _wrap(
                resolved_context.ResolvedContext.execute_shell
            )

            yield
        finally:
            resolved_context.ResolvedContext.execute_shell = original
