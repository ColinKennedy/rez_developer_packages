#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The main run-time tests for the ``sphinx_apidoc_check`` CLI."""

import os
import shlex
import shutil
import tempfile

from python_compatibility.testing import common
from sphinx_apidoc_check import cli
from sphinx_apidoc_check.core import check_exception


class Run(common.Common):
    """Make sure that ``sphinx_apidoc_check`` runs the way its expected."""

    def test_bad_arguments(self):
        """Error early if not incorrect arguments are passed to ``sphinx-apidoc``."""
        root = tempfile.mkdtemp(suffix="_some_test_python_package")
        self.add_item(root)

        with self.assertRaises(check_exception.InvalidSphinxArguments):
            cli.check("sphinx-apidoc", directory=root)

    def test_empty(self):
        """Test that a directory that exists but is empty just makes a modules.rst file."""
        root = tempfile.mkdtemp(suffix="_some_test_python_package")

        results = cli.check(
            _args(". --output-dir {root} --dry-run".format(root=root)), directory=root,
        )

        self.assertEqual(({os.path.join(root, "modules.rst")}, set(), set()), results)

    def test_missing_dry_run_flag(self):
        """Make sure every call to ``sphinx_apidoc_check`` has a --dry-run flag included."""
        root = tempfile.mkdtemp(suffix="_some_test_python_package")
        self.add_item(root)

        output = os.path.join(root, "documentation", "output")
        os.makedirs(output)

        with self.assertRaises(check_exception.NoDryRun):
            cli.check(
                _args(". --output-dir {output}".format(output=output)), directory=root
            )

    def test_nothing(self):
        """Test that a Python folder with nothing in it just reports the modules.rst file."""
        root = tempfile.mkdtemp(suffix="_some_test_python_package")
        self.add_item(root)
        output = os.path.join(root, "documentation", "output")
        results = cli.check(
            _args(". --output-dir {output} --dry-run".format(output=output)),
            directory=root,
        )

        self.assertEqual(({os.path.join(output, "modules.rst")}, set(), set()), results)

    def test_directory_does_not_exist(self):
        """If a directory is given that does not exist, error early."""
        root = tempfile.mkdtemp(suffix="_some_test_python_package")
        shutil.rmtree(root)

        with self.assertRaises(check_exception.DirectoryDoesNotExist):
            cli.check("sphinx-apidoc", directory=root)

    def test_added_files_001(self):
        """Check that a basic Python module gets reported as expected."""
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
        """Check that a basic Python module gets reported as expected."""
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
        """Tell the user to remove an existing .rst file if it has no equivalent Python file."""
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
        """Detect if a Python file + its .rst file already exists and report nothing."""
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


class Integrations(common.Common):
    """A test that calls the ``sphinx_apidoc_check`` CLI, directly."""

    def test_basic(self):
        """Test a basic run of ``sphinx_apidoc_check``."""
        pass

    def test_more_arguments(self):
        """Test that a variation of arguments still works."""
        pass

    def test_temporary_cd(self):
        """Make sure that the user's working directory stays the same."""
        pass

    def test_temporary_cd_error(self):
        """Make sure that the user's working directory stays the same even after erroring."""
        pass


def _args(text):
    """Split text into arguments, so that :func:`sphinx_apidoc_check.cli.check` can use it."""
    return shlex.split(text)
