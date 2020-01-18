#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The main run-time tests for the ``sphinx_apidoc_check`` CLI."""

import os
import shlex
import shutil
import subprocess
import tempfile
import textwrap

from python_compatibility.testing import common
from six.moves import mock
from sphinx_apidoc_check import cli
from sphinx_apidoc_check.core import check_exception

_CURRENT_DIRECTORY = os.path.dirname(os.path.realpath(__file__))


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

    @staticmethod
    def _get_command():
        rez_package_root = os.path.dirname(_CURRENT_DIRECTORY)

        return os.path.join(rez_package_root, "bin", "sphinx_apidoc_check")

    def _do_basic_run(self, template):
        structure = {
            "some_package": {
                "__init__.py": None,
                "something_inside": {"__init__.py": None, "some_module.py": None,},
            }
        }

        root = tempfile.mkdtemp(suffix="_some_test_python_package")
        self.add_item(root)
        common.make_files(structure, root)
        output = os.path.join(root, "documentation", "output")
        command = self._get_command()
        full_command = template.format(command=command, root=root, output=output)
        process = subprocess.Popen(
            _args(full_command), stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )

        stdout, stderr = process.communicate()

        return stdout, stderr, output

    def test_basic(self):
        """Test a basic run of ``sphinx_apidoc_check``."""
        stdout, stderr, output = self._do_basic_run(
            '{command} "{root} --output-dir {output} --dry-run"'
        )
        self.assertFalse(stderr)

        expected_template = textwrap.dedent(
            """\
            These files must be added:
            {file_1}
            {file_2}
            {file_3}
            Please re-run sphinx-apidoc to fix this
            """
        )

        self.assertEqual(
            expected_template.format(
                file_1=os.path.join(output, "modules.rst"),
                file_2=os.path.join(output, "some_package.rst"),
                file_3=os.path.join(output, "some_package.something_inside.rst"),
            ),
            stdout,
        )

    def test_more_arguments(self):
        """Test that a variation of arguments still works."""
        stdout, stderr, output = self._do_basic_run(
            '{command} "{root} --output-dir {output} --dry-run --separate"'
        )
        self.assertFalse(stderr)

        expected_template = textwrap.dedent(
            """\
            These files must be added:
            {file_1}
            {file_2}
            {file_3}
            {file_4}
            Please re-run sphinx-apidoc to fix this
            """
        )

        self.assertEqual(
            expected_template.format(
                file_1=os.path.join(output, "modules.rst"),
                file_2=os.path.join(output, "some_package.rst"),
                file_3=os.path.join(output, "some_package.something_inside.rst"),
                file_4=os.path.join(
                    output, "some_package.something_inside.some_module.rst"
                ),
            ),
            stdout,
        )

    def test_temporary_cd(self):
        """Make sure that the user's working directory stays the same."""
        current_directory = os.getcwd()

        some_directory = tempfile.mkdtemp(suffix="_some_directory")
        self.add_item(some_directory)
        _, stderr, _ = self._do_basic_run(
            '{{command}} "{{root}} --output-dir {{output}} --dry-run" --directory {some_directory}'.format(
                some_directory=some_directory
            )
        )

        self.assertFalse(stderr)
        self.assertEqual(current_directory, os.getcwd())

    @mock.patch("sphinx_apidoc_check.cli._get_apidoc_main_function")
    def test_temporary_cd_error(self, _get_apidoc_main_function):
        """Make sure that the user's working directory stays the same even after erroring."""
        current_directory = os.getcwd()
        _get_apidoc_main_function.raiseError.side_effect = mock.Mock(
            side_effect=Exception("Some exception.")
        )

        some_directory = tempfile.mkdtemp(suffix="_some_directory")
        self.add_item(some_directory)
        _, stderr, _ = self._do_basic_run(
            '{{command}} "{{root}} --output-dir {{output}} --dry-run" --directory {some_directory}'.format(
                some_directory=some_directory
            )
        )

        self.assertFalse(stderr)
        self.assertEqual(current_directory, os.getcwd())


def _args(text):
    """Split text into arguments, so that :func:`sphinx_apidoc_check.cli.check` can use it."""
    return shlex.split(text)
