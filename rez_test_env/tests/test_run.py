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
from rez_utilities import creator, finder, rez_configuration


class BuildRequires(unittest.TestCase):
    """Make sure build-related options work as expected."""

    def test_build_requires(self):
        """Include `build_requires` in the Rez resolve."""
        directory = _make_test_packages()

        build_directory = tempfile.mkdtemp(
            suffix="_BuildRequires_test_private_build_requires"
        )
        atexit.register(functools.partial(shutil.rmtree, build_directory))

        package_directory = os.path.join(directory, "package_b")

        creator.build(
            finder.get_nearest_rez_package(package_directory),
            build_directory,
            quiet=True,
            packages_path=[directory],
        )

        with _keep_pwd():
            os.chdir(package_directory)

            result = _test(
                "directory --directory '{directory}' unittest_* --build-requires".format(
                    directory=os.path.join(build_directory, "package_b", "1.1.0"),
                ),
                directory,
                build_directory=build_directory,
            )

        self.assertEqual({"build_a-1.2.0", "package_a", "package_b-1.1.0"}, result)

    def test_no_requires(self):
        """Allow the build requires flags even if the Rez package doesn't define them."""
        directory = _make_test_packages()

        build_directory = tempfile.mkdtemp(
            suffix="_BuildRequires_test_private_build_requires"
        )
        atexit.register(functools.partial(shutil.rmtree, build_directory))

        package_directory = os.path.join(directory, "package_a")

        creator.build(
            finder.get_nearest_rez_package(package_directory),
            build_directory,
            quiet=True,
            packages_path=[directory],
        )

        with _keep_pwd():
            os.chdir(package_directory)

            result = _test(
                "directory --directory '{directory}' name_A --build-requires --private-build-requires".format(
                    directory=os.path.join(build_directory, "package_a", "1.0.0"),
                ),
                directory,
                build_directory=build_directory,
            )

        self.assertEqual({"package_a-1.0.0", "package_d-1.1.0"}, result)

    def test_private_build_requires(self):
        """Include `private_build_requires` in the Rez resolve."""
        directory = _make_test_packages()

        build_directory = tempfile.mkdtemp(
            suffix="_BuildRequires_test_private_build_requires"
        )
        atexit.register(functools.partial(shutil.rmtree, build_directory))

        package_directory = os.path.join(directory, "package_b")

        creator.build(
            finder.get_nearest_rez_package(package_directory),
            build_directory,
            quiet=True,
            packages_path=[directory],
        )

        with _keep_pwd():
            os.chdir(package_directory)

            result = _test(
                "directory --directory '{directory}' unittest_* --private-build-requires".format(
                    directory=os.path.join(build_directory, "package_b", "1.1.0"),
                ),
                directory,
                build_directory=build_directory,
            )

        self.assertEqual({"build_b-1.4.0", "package_a", "package_b-1.1.0"}, result)


class Run(unittest.TestCase):
    """Run the `rez_test_env` code as if a user wrote it through the CLI."""

    def test_no_tests(self):
        """Allow `rez_test_env` to be called with no additional rez-test commands."""
        directory = _make_test_packages()

        resolved = _test("request package_a", directory)

        self.assertEqual({"package_a"}, resolved)

    def test_unittest_names(self):
        """Make sure 1-or-more rez-test commands are allowed as input."""
        directory = _make_test_packages()

        single = _test("request package_a name_A", directory)
        multiple = _test("request package_a name_A name_B", directory)

        self.assertEqual({"package_a", "package_d-1.1.0"}, single)
        self.assertEqual({"package_a", "package_d-1.1.0", "package_c"}, multiple)

    def test_glob(self):
        """Make sure glob expressions work."""
        directory = _make_test_packages()

        multiple = _test("request package_a name_*", directory)

        self.assertEqual({"package_a", "package_d-1.1.0", "package_c"}, multiple)

    def test_from_package_directory(self):
        """Get the resolve from a package's directory."""
        directory = _make_test_packages()

        build_directory = tempfile.mkdtemp(suffix="_Run_test_from_package_directory")
        atexit.register(functools.partial(shutil.rmtree, build_directory))

        package_directory = os.path.join(directory, "package_b")

        creator.build(
            finder.get_nearest_rez_package(package_directory),
            build_directory,
            quiet=True,
        )

        result = _test(
            "directory --directory '{directory}' unittest_*".format(
                directory=os.path.join(build_directory, "package_b", "1.1.0"),
            ),
            directory,
            build_directory=build_directory,
        )

        self.assertEqual({"package_a", "package_b-1.1.0"}, result)

    def test_from_package_pwd(self):
        """Get the resolve from a package's directory."""
        directory = _make_test_packages()
        package_directory = os.path.join(directory, "package_b")

        build_directory = tempfile.mkdtemp(suffix="_Run_test_from_package_pwd")
        atexit.register(functools.partial(shutil.rmtree, build_directory))

        creator.build(
            finder.get_nearest_rez_package(package_directory),
            build_directory,
            quiet=True,
        )

        with _keep_pwd():
            os.chdir(package_directory)

            result = _test(
                "directory unittest_*",
                directory,
                build_directory=build_directory,
            )

        self.assertEqual({"package_a", "package_b-1.1.0"}, result)


class Invalids(unittest.TestCase):
    """Make sure the CLI will fail if the user provides bad input."""

    def test_package_name(self):
        """Raise an exception if the given Rez package doesn't exist."""
        with self.assertRaises(exceptions.NoValidPackageFound):
            _test("request does_not_exist_package_name", tempfile.gettempdir())

    def test_test_names(self):
        """Raise an exception if any of the given Rez test commands don't exist."""
        directory = _make_test_packages()

        with self.assertRaises(exceptions.MissingTests):
            _test("request package_a does_not_exist", directory)


def _make_test_packages():
    """Create a few (very hacky and fake) Rez packages to use for testing."""

    def _make_quick_package(name, version):
        package = os.path.join(directory, name, version)
        os.makedirs(package)

        with open(os.path.join(package, "package.py"), "w") as handler:
            handler.write(
                'name = "{name}"\nversion = "{version}"'.format(
                    name=name, version=version
                )
            )

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

                build_command = 'echo "package_a has been built!"'

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

                build_command = 'echo "package_b has been built!"'

                private_build_requires = ["build_b-1"]

                build_requires = ["build_a-1"]

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

    _make_quick_package("build_a", "1.2.0")
    _make_quick_package("build_b", "1.4.0")
    _make_quick_package("package_d", "1.1.0")
    _make_quick_package("package_c", "2.0.0")

    return directory


@contextlib.contextmanager
def _override_context_command():
    """Change Rez's context function to always print out a Rez resolve.

    This function is a bit strange. Basically, `rez_test_env` always
    gives the user a new shell to run commands in. But for testing,
    this is bad because we actually want to know the resolved Rez
    packages. So instead of modifying `rez_test_env` with clutter
    to make that possible, we simply tell Rez to always echo the
    REZ_RESOLVE environment variable.

    Yields:
        callable: The overwritten :meth:`rez.resolved_context.ResolvedContext.execute_shell` method.

    """

    def _wrap(function):
        @functools.wraps(function)
        def wrapper(*args, **kwargs):
            """Append a command to print the resolved packages, then run ``function``."""
            system = platform.system()

            if system == "Windows":
                kwargs["command"] = "echo %REZ_RESOLVE%"
            elif system == "Linux":
                kwargs["command"] = "echo $REZ_RESOLVE"
            else:
                raise NotImplementedError(
                    'System "{system}" is not supported yet.'.format(system=system)
                )

            return function(*args, **kwargs)

        return wrapper

    original = resolved_context.ResolvedContext.execute_shell

    try:
        resolved_context.ResolvedContext.execute_shell = _wrap(
            resolved_context.ResolvedContext.execute_shell
        )

        yield
    finally:
        resolved_context.ResolvedContext.execute_shell = original


@contextlib.contextmanager
def _keep_pwd():
    """Save and restore the current $PWD of the user."""
    original = os.getcwd()

    try:
        yield
    finally:
        os.chdir(original)


def _test(request, directory, build_directory=""):
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
        build_directory (str, optional): If provided, this path is added to resolves. Default: "".

    Returns:
        set[str]: The resolved Rez packages/versions.

    """
    packages_path = [directory]

    if build_directory:
        packages_path += [build_directory]

    with _override_context_command():
        with rez_configuration.patch_packages_path(packages_path):
            try:
                with wurlitzer.pipes() as (
                    stdout,
                    stderr,
                ):  # wurlitzer will capture stdout
                    cli.main(shlex.split(request))
            except SystemExit as error:
                # Since `rez_test_env` literally runs the `rez-env` CLI
                # as part of its work, it always raises a `SystemExit`
                # exception. So we catch that and only re-raise if there
                # was actually an error.
                #
                if error.code != 0:
                    raise

    data = set(stdout.read().strip().split())

    stdout.close()
    stderr.close()

    return data
