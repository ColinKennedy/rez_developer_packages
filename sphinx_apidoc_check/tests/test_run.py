#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import shlex
import shutil
import tempfile
import unittest

from python_compatibility.testing import common

from sphinx_apidoc_check import cli
from sphinx_apidoc_check.core import check_exception


class Run(common.Common):
    def test_bad_arguments(self):
        root = tempfile.mkdtemp(suffix="_some_test_python_package")
        self.add_item(root)

        with self.assertRaises(check_exception.InvalidSphinxArguments):
            cli.check("sphinx-apidoc", directory=root)

    def test_empty(self):
        # This should error
        pass

    def test_nothing(self):
        root = tempfile.mkdtemp(suffix="_some_test_python_package")
        self.add_item(root)
        output = os.path.join(root, "documentation", "output")
        results = cli.check(_args('. --output-dir {output} --dry-run'.format(output=output)), directory=root)

        self.assertEqual(({os.path.join(output, "modules.rst")}, set()), results)

    def test_missing_dry_run_flag(self):
        root = tempfile.mkdtemp(suffix="_some_test_python_package")
        self.add_item(root)

        output = os.path.join(root, "documentation", "output")
        os.makedirs(output)

        with self.assertRaises(check_exception.NoDryRun):
            cli.check(_args('. --output-dir {output}'.format(output=output)), directory=root)

    def test_directory_does_not_exist(self):
        root = tempfile.mkdtemp(suffix="_some_test_python_package")
        shutil.rmtree(root)

        with self.assertRaises(check_exception.DirectoryDoesNotExist):
            cli.check("sphinx-apidoc", directory=root)

    def test_added_files(self):
        structure = {
            "python": {
                "some_package": {
                    "__init__.py": dict(),
                    "some_module.py": dict(),
                }
            },
        }

        root = tempfile.mkdtemp(suffix="_some_test_python_package")
        self.add_item(root)
        common.make_files(structure)
        output = os.path.join(root, "documentation", "output")
        results = cli.check(_args('. --output-dir {output} --dry-run'.format(output=output)), directory=root)

        added = {
            os.path.join(output, "modules.rst"),
            os.path.join(output, "some_package", "some_module.rst"),
            os.path.join(output, "some_package.rst"),
        }

        self.assertEqual((added, set()), results)


    def test_removed_files(self):
        pass

    def test_changed_files(self):
        pass

    def test_new_arguments(self):
        pass


def _args(text):
    return shlex.split(text)
