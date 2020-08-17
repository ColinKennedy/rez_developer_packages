#!/usr/bin/env python
# -*- coding: utf-8 -*-

import atexit
import contextlib
import functools
import os
import shlex
import shutil
import tempfile
import textwrap
import unittest
import sys


from six.moves import cStringIO
from rez import resolved_context
from rez_utilities import rez_configuration
import wurlitzer

from rez_test_env.core import exceptions
from rez_test_env import cli


class Run(unittest.TestCase):
    def test_no_tests(self):
        directory = _make_test_packages()

        resolved = _test("package_a", directory)

        raise ValueError(resolved)

    def test_unittest_names(self):
        directory = _make_test_packages()

        single = _test("package_a name_A", directory)
        multiple = _test("package_a name_A name_B", directory)

        self.assertEqual({"package_d-1.1.0"}, single)
        self.assertEqual({"package_d-1.1.0", "package_c"}, multiple)

    def test_glob(self):
        directory = _make_test_packages()

        multiple = _test("package_a name_*", directory)

        self.assertEqual({"package_d-1.1.0", "package_c"}, multiple)


class Invalids(unittest.TestCase):
    def test_package_name(self):
        with self.assertRaises(exceptions.NoValidPackageFound):
            _test("does_not_exist_package_name", tempfile.gettempdir())

    def test_test_names(self):
        directory = _make_test_packages()

        with self.assertRaises(exceptions.MissingTests):
            _test("package_a does_not_exist", directory)


def _make_test_packages():
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
    with _override_context_command():
        with rez_configuration.patch_packages_path([directory]):
            try:
                with wurlitzer.pipes() as (stdout, _):
                    cli.main(shlex.split(request))
            except SystemExit as error:
                if error.code != 0:
                    raise


    return set(stdout.read().strip().split())
