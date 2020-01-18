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
        """Test that a directory that exists but is empty just makes a modules.rst file."""
        root = tempfile.mkdtemp(suffix="_some_test_python_package")

        results = cli.check(
            _args(". --output-dir {root} --dry-run".format(root=root)),
            directory=root,
        )

        self.assertEqual(({os.path.join(root, "modules.rst")}, set(), set()), results)

    def test_missing_dry_run_flag(self):
        root = tempfile.mkdtemp(suffix="_some_test_python_package")
        self.add_item(root)

        output = os.path.join(root, "documentation", "output")
        os.makedirs(output)

        with self.assertRaises(check_exception.NoDryRun):
            cli.check(
                _args(". --output-dir {output}".format(output=output)), directory=root
            )

    def test_nothing(self):
        root = tempfile.mkdtemp(suffix="_some_test_python_package")
        self.add_item(root)
        output = os.path.join(root, "documentation", "output")
        results = cli.check(
            _args(". --output-dir {output} --dry-run".format(output=output)),
            directory=root,
        )

        self.assertEqual(({os.path.join(output, "modules.rst")}, set(), set()), results)

    def test_directory_does_not_exist(self):
        root = tempfile.mkdtemp(suffix="_some_test_python_package")
        shutil.rmtree(root)

        with self.assertRaises(check_exception.DirectoryDoesNotExist):
            cli.check("sphinx-apidoc", directory=root)

    def test_added_files_001(self):
        structure = {"some_package": {"__init__.py": None, "some_module.py": None,}}

        root = tempfile.mkdtemp(suffix="_some_test_python_package")
        self.add_item(root)
        common.make_files(structure, root)
        output = os.path.join(root, "documentation", "output")
        results = cli.check(
            _args(
                "{root} --output-dir {output} --dry-run".format(
                    root=root, output=output
                )
            ),
            directory=root,
        )

        added = {
            os.path.join(output, "modules.rst"),
            os.path.join(output, "some_package.rst"),
        }

        self.assertEqual((added, set(), set()), results)

    def test_added_files_002(self):
        structure = {"some_package": {"__init__.py": None, "some_module.py": None,}}

        root = tempfile.mkdtemp(suffix="_some_test_python_package")
        self.add_item(root)
        common.make_files(structure, root)
        output = os.path.join(root, "documentation", "output")
        results = cli.check(
            _args(
                "{root} --output-dir {output} --dry-run --separate".format(
                    root=root, output=output
                )
            ),
            directory=root,
        )

        added = {
            os.path.join(output, "modules.rst"),
            os.path.join(output, "some_package.some_module.rst"),
            os.path.join(output, "some_package.rst"),
        }

        self.assertEqual((added, set(), set()), results)

    def test_added_files_003(self):
        """Check that existing API files don't get returned. Only new API files."""
        structure = {"some_package": {"__init__.py": None, "some_module.py": None,}}

        root = tempfile.mkdtemp(suffix="_some_test_python_package")
        self.add_item(root)
        common.make_files(structure, root)
        output = os.path.join(root, "documentation", "output")
        os.makedirs(output)
        existing_file = os.path.join(output, "some_package.rst")
        open(existing_file, "a").close()

        results = cli.check(
            _args(
                "{root} --output-dir {output} --dry-run --separate".format(
                    root=root, output=output
                )
            ),
            directory=root,
        )

        added = {
            os.path.join(output, "modules.rst"),
            os.path.join(output, "some_package.some_module.rst"),
        }

        self.assertEqual((added, {existing_file}, set()), results)

    def test_removed_files(self):
        structure = {"some_package": {"__init__.py": None,}}

        root = tempfile.mkdtemp(suffix="_some_test_python_package")
        self.add_item(root)
        common.make_files(structure, root)
        output = os.path.join(root, "documentation", "output")
        os.makedirs(output)
        existing_file = os.path.join(output, "some_package.some_module.rst")
        open(existing_file, "a").close()

        results = cli.check(
            _args(
                "{root} --output-dir {output} --dry-run".format(
                    root=root, output=output
                )
            ),
            directory=root,
        )

        added = {
            os.path.join(output, "modules.rst"),
            os.path.join(output, "some_package.rst"),
        }

        self.assertEqual((added, set(), {existing_file}), results)

    def test_changed_files(self):
        structure = {"some_package": {"__init__.py": None,}}

        root = tempfile.mkdtemp(suffix="_some_test_python_package")
        self.add_item(root)
        common.make_files(structure, root)
        output = os.path.join(root, "documentation", "output")
        os.makedirs(output)
        existing_file = os.path.join(output, "some_package.rst")
        open(existing_file, "a").close()

        results = cli.check(
            _args(
                "{root} --output-dir {output} --dry-run".format(
                    root=root, output=output
                )
            ),
            directory=root,
        )

        added = {
            os.path.join(output, "modules.rst"),
        }

        self.assertEqual((added, {existing_file}, set()), results)


def _args(text):
    return shlex.split(text)
