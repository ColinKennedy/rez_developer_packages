#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""All tests related to building, collapsing, and symlinking HDAs."""

from __future__ import unicode_literals

import atexit
import functools
import io
import os
import platform
import shutil
import tempfile
import textwrap

from rez_build_helper import filer

from .common import common, creator, finder, pymix


class Hda(common.Common):
    """All tests related to building Houdini HDAs."""

    def test_which(self) -> None:
        """Make sure the we get the hotl correctly.

        This path is only used for testing. In production, this should
        point to a Houdini ``hotl`` binary file.

        """
        expected = os.path.join(
            os.environ["REZ_REZ_BUILD_HELPER_ROOT"],
            "fake_bin",
            "hotl",
        )

        if platform.system() == "Windows":
            expected = expected + ".bat"

        self.assertEqual(
            expected,
            filer._get_hotl_executable(),  # pylint: disable=protected-access
        )

    def test_collapse(self) -> None:
        """Collapse a HDA VCS folder into a single HDA file.

        This test doesn't actually do the collapse. But it tests the
        logic which would do it.

        """
        directory = tempfile.mkdtemp(
            prefix="rez_build_helper_Hda_test_collapse_source_directory_",
        )
        atexit.register(functools.partial(shutil.rmtree, directory))

        common.make_files(
            {"hda": {"blah": {"houdini.hdalibrary": None}}},
            directory,
        )

        with io.open(
            os.path.join(directory, "package.py"), "w", encoding="ascii"
        ) as handler:
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

        creator.build(package, destination, quiet=True)

        install_location = os.path.join(destination, "some_package", "1.0.0")
        self.assertTrue(
            os.path.isfile(os.path.join(install_location, "hda", "blah", "hotl.txt"))
        )
        self.assertTrue(os.path.isdir(os.path.join(install_location, "hda", "blah")))

        if pymix.can_check_links():
            self.assertFalse(
                os.path.islink(os.path.join(install_location, "hda", "blah"))
            )

    def test_symlink(self) -> None:
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

        with io.open(
            os.path.join(directory, "package.py"), "w", encoding="ascii"
        ) as handler:
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

        creator.build(package, destination, quiet=True)

        install_location = os.path.join(destination, "some_package", "1.0.0")
        self.assertFalse(os.path.isfile(os.path.join(install_location, "hotl.txt")))
        hda = os.path.join(install_location, "hda")
        files = os.listdir(hda)

        for item in files:
            path = os.path.join(hda, item)

            if pymix.can_check_links():
                self.assertTrue(os.path.islink(path))

        self.assertEqual(["blah"], files)
