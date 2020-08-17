#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The main tests for `rez_test_env`, specifically for different CLI situations."""

import atexit
import contextlib
import functools
import os
import platform
import shlex
import shutil
import tempfile
import textwrap
import unittest

import wurlitzer
from rez import resolved_context
from rez_test_env import cli
from rez_test_env.core import exceptions
from rez_utilities import rez_configuration
from six.moves import cStringIO


class Run(unittest.TestCase):
    """Run the `rez_test_env` code as if a user wrote it through the CLI."""

    def test_no_tests(self):
        """Allow `rez_test_env` to be called with no additional rez-test commands."""
        directory = _make_test_packages()

        resolved = _test("package_a", directory)

        raise ValueError(resolved)

    def test_unittest_names(self):
        """Make sure 1-or-more rez-test commands are allowed as input."""
        directory = _make_test_packages()

        single = _test("package_a name_A", directory)
        multiple = _test("package_a name_A name_B", directory)

        self.assertEqual({"package_d-1.1.0"}, single)
        self.assertEqual({"package_d-1.1.0", "package_c"}, multiple)

    def test_glob(self):
        """Make sure glob expressions work."""
        directory = _make_test_packages()

        multiple = _test("package_a name_*", directory)

        self.assertEqual({"package_d-1.1.0", "package_c"}, multiple)


class Invalids(unittest.TestCase):
    """Make sure the CLI will fail if the user provides bad input."""

    def test_package_name(self):
        """Raise an exception if the given Rez package doesn't exist."""
        with self.assertRaises(exceptions.NoValidPackageFound):
            _test("does_not_exist_package_name", tempfile.gettempdir())

    def test_test_names(self):
        """Raise an exception if any of the given Rez test commands don't exist."""
        directory = _make_test_packages()

        with self.assertRaises(exceptions.MissingTests):
            _test("package_a does_not_exist", directory)


def _make_test_packages():
    """Create a few (very hacky and fake) Rez packages to use for testing."""
    directory = tempfile.mkdtemp(prefix="rez_test_env_package_")
    atexit.register(functools.partial(shutil.rmtree, directory))

    package_a = os.path.join(directory, "package_a")
    os.makedirs(package_a)

    with open(os.path.join(package_a, "package.py"), "w") as handler:
        handler.write(
            textwrap.dedent(
                """\
                name = "package_a"

                version = "1.0.0"

                tests = {
                    "name_A": {
                        "command": "echo 'foo'",
                        "requires": ["package_d-1+<2"],
                    },
                    "name_B": {
                        "command": "echo 'bar'",
                        "requires": ["package_c"],
                    }
                }
                """
            )
        )

    package_b = os.path.join(directory, "package_b")
    os.makedirs(package_b)

    with open(os.path.join(package_b, "package.py"), "w") as handler:
        handler.write(
            textwrap.dedent(
                """\
                name = "package_b"

                version = "1.1.0"

                tests = {
                    "unittest_1": {
                        "command": "echo 'Something'",
                        "requires": ["package_a"],
                    },
                    "unittest_2": "echo 'Blah'",
                }
                """
            )
        )

    package_d = os.path.join(directory, "package_d", "1.1.0")
    os.makedirs(package_d)

    with open(os.path.join(package_d, "package.py"), "w") as handler:
        handler.write(
            textwrap.dedent(
                """\
                name = "package_d"

                version = "1.1.0"
                """
            )
        )

    package_c = os.path.join(directory, "package_c")
    os.makedirs(package_c)

    with open(os.path.join(package_c, "package.py"), "w") as handler:
        handler.write(
            textwrap.dedent(
                """\
                name = "package_c"

                version = "2.0.0"
                """
            )
        )

    return directory


@contextlib.contextmanager
def _override_context_command():
    def _wrap(function):
        @functools.wraps(function)
        def wrapper(*args, **kwargs):
            kwargs["command"] = "echo $REZ_RESOLVE"

            return function(*args, **kwargs)

        return wrapper

    original = resolved_context.ResolvedContext.execute_shell

    try:
        resolved_context.ResolvedContext.execute_shell = _wrap(resolved_context.ResolvedContext.execute_shell)

        yield
    finally:
        resolved_context.ResolvedContext.execute_shell = original


def _test(request, directory):
    """Test a CLI command for `rez_test_env` and get its resolved packages back.

    This function is a bit intense so let's break it down.

    The goal of this function is to

    - Get resolved Rez packages
    - Make a test environment that will work regardless of the user's
      actual Rez environment.
    - Be as quiet (not-spammy) as possible

    Args:
        request (str): User-provided test which would be sent directly to the CLI.
        directory (str): The folder on-disk where the fake Rez package(s) for the test live.

    Returns:
        set[str]: The resolved Rez packages/versions.

    """
    with _override_context_command():
        with rez_configuration.patch_packages_path([directory]):
            try:
                with wurlitzer.pipes() as (stdout, _):  # wurlitzer will capture stdout
                    cli.main(shlex.split(request))
            except SystemExit as error:
                # Since `rez_test_env` literally runs the `rez-env` CLI
                # as part of its work, it always raises a `SystemExit`
                # exception. So we catch that and only re-raise if there
                # was actually an error.
                #
                if error.code != 0:
                    raise

    return set(stdout.read().strip().split())
