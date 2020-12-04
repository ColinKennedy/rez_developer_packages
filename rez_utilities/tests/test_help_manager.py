#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Make sure :mod:`rez_utilities.help_manager` works as expected."""

import atexit
import functools
import json
import os
import shutil
import subprocess
import tempfile
import textwrap
import unittest

from rez_utilities import help_manager

try:
    from rez import package_maker
except ImportError:
    from rez import package_maker__ as package_maker

try:
    from rez import packages as packages_
except ImportError:
    from rez import packages_


class GetHelpData(unittest.TestCase):
    """Make sure :func:`rez_utilities.help_manager.get_data` works."""

    def test_directory_implicit(self):
        """Get the Rez package automatically (without setting a directory)."""
        help_ = [["Something", "foo/bar.txt"]]
        package = _make_package(help_=help_)
        everything = _get_package_help(os.path.dirname(package.filepath))
        self.assertEqual(help_, everything)

    def test_empty_list(self):
        """Get `help` from a Rez package with a defined, empty `help` attribute."""
        help_ = []
        package = _make_package(help_=help_)
        items = help_manager.get_data(os.path.dirname(package.filepath))

        self.assertEqual([], items)

    def test_empty_string(self):
        """Get `help` from a Rez package with a defined, empty `help` attribute."""
        help_ = ""
        package = _make_package(help_=help_)
        items = help_manager.get_data(os.path.dirname(package.filepath))

        self.assertEqual([], items)

    def test_invalid_001(self):
        """Fail early because the directory does not exist."""
        directory = tempfile.mkdtemp(suffix="_does_not_exist")
        shutil.rmtree(directory)

        with self.assertRaises(ValueError):
            help_manager.get_data(directory)

    def test_invalid_002(self):
        """Fail early because the directory is not in a Rez package."""
        directory = tempfile.mkdtemp(suffix="_does_not_exist")
        atexit.register(functools.partial(shutil.rmtree, directory))

        with self.assertRaises(RuntimeError):
            help_manager.get_data(directory)

    def test_list_001(self):
        """Get help path data from a list."""
        help_ = [["Some Text", "and/more/things"]]
        package = _make_package(help_=help_)
        items = help_manager.get_data(os.path.dirname(package.filepath))

        self.assertEqual(help_, items)

    def test_list_002(self):
        """Get multiple help URLs from a list."""
        help_ = [
            ["Some Documentation", "http://www.some_path_here_does_not_exist.com"],
            ["Another Documentation", "http://www.another_path_that_is_not_real.com"],
        ]
        package = _make_package(help_=help_)
        items = help_manager.get_data(os.path.dirname(package.filepath))

        self.assertEqual(help_, items)

    def test_matches_custom(self):
        """Use a custom `matches` argument to get help information."""

        def _matches(key):
            return key.lower() == "blah"

        help_ = [["Blah", "some/non/existent/path"]]
        package = _make_package(help_=help_)
        items = help_manager.get_data(
            os.path.dirname(package.filepath),
            matches=_matches,
        )

        self.assertEqual(help_, items)

    def test_matches_empty(self):
        """Match nothing because there were no matches."""
        help_ = [["Blah", "some/non/existent/path"]]
        package = _make_package(help_=help_)
        items = help_manager.get_data(
            os.path.dirname(package.filepath),
            matches="*Thing*",
        )

        self.assertEqual([], items)

    def test_matches_glob_fail(self):
        """Match only one thing."""
        help_ = [
            ["Blah", "some/non/existent/path"],
            ["Some Documentation", "foo/bar"],
        ]
        package = _make_package(help_=help_)
        items = help_manager.get_data(
            os.path.dirname(package.filepath),
            matches="*Documentation",
        )

        self.assertEqual([["Some Documentation", "foo/bar"]], items)

    def test_matches_glob_find(self):
        """Get everything, via a glob."""
        help_ = [
            ["Blah", "some/non/existent/path"],
            ["Some Documentation", "foo/bar"],
        ]
        package = _make_package(help_=help_)
        items = help_manager.get_data(
            os.path.dirname(package.filepath),
            matches="*",
        )

        self.assertEqual(help_, items)

    def test_non_existent_path_001(self):
        """Don't resolve to an absolute path because the path doesn't exist."""
        help_ = [["Something", "some/non/existent/path"]]
        package = _make_package(help_=help_)
        items = help_manager.get_data(os.path.dirname(package.filepath))

        self.assertEqual(help_, items)

    def test_non_existent_path_002(self):
        """Don't resolve to an absolute path because the user asked not to."""
        directory = tempfile.mkdtemp(suffix="_GetHelpData_test_non_existent_path_002")
        os.makedirs(os.path.join(directory, "inner_folder"))

        with open(os.path.join(directory, "package.py"), "w") as handler:
            handler.write(
                textwrap.dedent(
                    """\
                    name = "some_package"

                    help = [
                        ["README", "inner_folder/README.md"]
                    ]
                    """
                )
            )

        path = os.path.join(directory, "inner_folder", "README.md")
        open(path, "a").close()

        self.assertEqual(
            [["README", path]],
            help_manager.get_data(directory),
        )
        self.assertEqual(
            [["README", "inner_folder/README.md"]],
            help_manager.get_data(directory, resolve=False),
        )

    def test_string_001(self):
        """Get help path data from a string."""
        help_ = tempfile.mkstemp(suffix="_test_string_001")[1]
        package = _make_package(help_=help_)
        items = help_manager.get_data(os.path.dirname(package.filepath))

        self.assertEqual([["Home Page", help_]], items)

    def test_string_002(self):
        """Get help URL data from a string."""
        help_ = "http://some_place_with_url.com"
        package = _make_package(help_=help_)
        items = help_manager.get_data(os.path.dirname(package.filepath))

        self.assertEqual([["Home Page", help_]], items)


def _get_package_help(directory):
    """Create a Python file and then import + run it in a subprocess.

    This function is a bit weird.

    :func:`rez_utilities.help_manager.get_data` is able to "auto
    find" the location of where it was called from in order to get a
    parent Rez package. But to do that without accidentally returning
    :mod:`rez_utilities`, we need to interrupt the call stack.

    We do this by running the module in a subprocess and then returning
its output. It's hacky, but it works.

    Args:
        directory (str):
            The absolute path to a folder on-disk. This folder is
            expected to have a Rez package defined inside of it.

    Returns:
        list[list[str, str]]: The found help documentation, if any.

    """
    path = os.path.join(directory, "some_file.py")

    with open(path, "w") as handler:
        handler.write(
            textwrap.dedent(
                """\
                from rez_utilities import help_manager

                print(repr(help_manager.get_data()))
                """
            )
        )

    process = subprocess.Popen(["python", path], stdout=subprocess.PIPE)
    stdout, _ = process.communicate()
    output = stdout.decode("utf-8").strip()
    cleaned = output.replace("u'", "'").replace("'", '"')

    return json.loads(cleaned)


def _make_package(help_=tuple()):
    """Make a Rez package with the given help attribute for testing.

    Args:
        help_ (str or list[list[str, str]]):
            A single help string or a list of display + help string
            pairs. The left of the pair is the text users might see. The
            right side is either an absolute or relative path on-disk or
            a website URL.

    Returns:
        :class:`rez.packages.DeveloperPackage`: The generated package.

    """
    directory = tempfile.mkdtemp(suffix="_make_package")
    atexit.register(functools.partial(shutil.rmtree, directory))

    name = "does_not_matter"
    version = "1.0.0"

    with package_maker.make_package(name, directory) as maker:
        maker.name = name
        maker.version = version
        maker.help = help_

    return packages_.get_developer_package(os.path.join(directory, name, version))
