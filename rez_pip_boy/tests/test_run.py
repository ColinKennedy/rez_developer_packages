#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Check to make sure ``rez_pip_boy`` makes "source" Rez pip packages as we expect."""

import atexit
import functools
import shutil
import tempfile
import subprocess
import inspect
import os
import unittest

from rez_pip_boy.core import _build_command

_BUILD_COMMAND_CODE = inspect.getsource(_build_command)


class Integrations(unittest.TestCase):
    """Build source Rez packages, using Rez-generated pip packages."""

    def _verify_source_package(self, installed_directory):
        package = os.path.join(installed_directory, "package.py")
        rezbuild = os.path.join(installed_directory, "rezbuild.py")

        with open(rezbuild, "r") as handler:
            rezbuild_code = handler.read()

        with open(package, "r") as handler:
            package_code = handler.readlines()

        self.assertEqual(_BUILD_COMMAND_CODE, rezbuild_code)
        self.assertIn("build_command = 'python {root}/rezbuild.py'\n", package_code)

    def test_simple(self):
        """Install a really simple pip package (a package with no dependencies)."""
        directory = tempfile.mkdtemp(prefix="rez_pip_boy_", suffix="_test_simple")
        atexit.register(functools.partial(shutil.rmtree, directory))

        _run_command('rez_pip_boy "--install six==1.14.0 --python-version=2.7" {directory}'.format(directory=directory))

        installed_directory = os.path.join(directory, "six", "1.14.0")
        self._verify_source_package(installed_directory)

    def test_complex_001(self):
        """Install a package with many dependencies and make sure each one is installed."""
        pass

    # def test_complex_002(self):
    #     """Install another package."""
    #     pass
    #
    # def test_recurring(self):
    #     """Install a package and then install the same package again."""
    #     pass
    #
    # def test_partial_install(self):
    #     """Install a package, delete one of its depedencies, and then install it again."""
    #     pass
    #
    # def test_hashed_variants(self):
    #     """Make sure hashed variants work."""
    #     pass
    #
    # def test_regular_variants(self):
    #     """Make sure non-hashed variants work."""
    #     pass


def _run_command(command):
    subprocess.call(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
