"""Make sure the :ref:`rez_dependency CLI` works as expected."""

from __future__ import print_function

import os
import shlex
import textwrap
import unittest

import six
from rez import exceptions as rez_exceptions
from rez.vendor.version import util
from six.moves import mock

from rez_dependency import cli
from rez_dependency._core import exception

_CURRENT_DIRECTORY = os.path.dirname(os.path.realpath(__file__))
_ROOT_DIRECTORY = os.path.dirname(_CURRENT_DIRECTORY)
_SIMPLE_PACKAGES = os.path.join(_ROOT_DIRECTORY, "_test_data", "simple_packages")
_VARIANT_EXAMPLE = os.path.join(_ROOT_DIRECTORY, "_test_data", "variant_example")


class Cases(unittest.TestCase):
    """Common scenarios should behave as expected."""

    def test_empty(self):
        """Allow null display."""
        result = _test(["list", "empty", "--packages-path", _SIMPLE_PACKAGES])

        self.assertEqual(["empty"], result)

    def test_nested(self):
        """Display a tree of nested dependencies."""
        result = _test(["tree", "nested", "--packages-path", _SIMPLE_PACKAGES])[0]

        expected = textwrap.dedent(
            """\
            nested:
                empty
                parent_package:
                    has_dependency:
                        empty"""
        )
        self.assertEqual(expected, result)


class Invalid(unittest.TestCase):
    """Fail expected scenarios in an expected way."""

    def test_bad_syntax(self):
        """Fail early if a request is an invalid syntax."""
        with self.assertRaises(util.VersionError):
            _test("list 'not-valid-syntax.xhere!'")

    def test_duplicate_family(self):
        """Prevent more than one package listed in the same request.

        It'd be difficult to generate a reliable set of dependencies for both
        since we collect everything into one Rez context. So we disallow this
        case.

        """
        with self.assertRaises(exception.UserInputError):
            _test(
                ["list", "empty-1", "empty==1.0.0", "--packages-path", _SIMPLE_PACKAGES]
            )

    def test_not_found(self):
        """Raise exceptions as expected when a request cannot be found."""
        with self.assertRaises(rez_exceptions.PackageFamilyNotFoundError):
            _test("list not_found_package_family")


class Skip(unittest.TestCase):
    """Skip displaying certain Rez package request elements.

    For example, ephemeral packages aren't "real" packages. They influence a
    resolve but they aren't actually a dependency in the same way that a proper
    installed Rez package is.

    """

    def test_conflicted_001_in_request(self):
        """Skip conflict package display, because they aren't "real" dependencies."""
        result = _test(
            ["list", "empty-1", "!foo-2", "--packages-path", _SIMPLE_PACKAGES]
        )

        self.assertEqual(["empty"], result)

    def test_conflicted_002_in_requires(self):
        """Skip conflict package display, because they aren't "real" dependencies."""
        result = _test(
            ["list", "has_conflict_package==1.0.0", "--packages-path", _SIMPLE_PACKAGES]
        )

        self.assertEqual(["has_conflict_package"], result)

    def test_ephemerals_001_in_request(self):
        """Skip ephemeral package display, because they aren't "real" dependencies."""
        result = _test(
            [
                "list",
                "empty-1",
                ".some_ephemeral-1",
                "--packages-path",
                _SIMPLE_PACKAGES,
            ]
        )

        self.assertEqual(["empty"], result)

    def test_ephemerals_002_in_requires(self):
        """Skip ephemeral package display, because they aren't "real" dependencies."""
        result = _test(
            ["list", "contains_ephemeral-1", "--packages-path", _SIMPLE_PACKAGES]
        )

        self.assertEqual(["contains_ephemeral"], result)


class Variants(unittest.TestCase):
    """Make sure variant requires are reported correctly."""

    def test_levels(self):
        """Make sure :ref:`levels sub-command` reports variants."""
        result = _test(["levels", "nested", "--packages-path", _VARIANT_EXAMPLE])[0]

        expected = textwrap.dedent(
            """\
            #0: nested
            #1: empty parent_package
            #2: has_dependency some_package
            #3: empty"""
        )

        self.assertEqual(expected, result)

    def test_list(self):
        """Make sure :ref:`list sub-command` reports variants."""
        result = _test(["list", "nested", "--packages-path", _VARIANT_EXAMPLE])[0]

        expected = textwrap.dedent(
            """\
            empty
            has_dependency
            nested
            parent_package
            some_package"""
        )
        self.assertEqual(expected, result)

    def test_tree_001(self):
        """Make sure :ref:`tree sub-command` reports variants."""
        result = _test(["tree", "parent_package", "--packages-path", _VARIANT_EXAMPLE])[
            0
        ]

        expected = textwrap.dedent(
            """\
            parent_package:
                has_dependency:
                    empty
                some_package"""
        )
        self.assertEqual(expected, result)

    def test_tree_002(self):
        """Make sure :ref:`tree sub-command` reports variants."""
        result = _test(["tree", "nested", "--packages-path", _VARIANT_EXAMPLE])[0]

        expected = textwrap.dedent(
            """\
            nested:
                empty
                parent_package:
                    has_dependency:
                        empty
                    some_package"""
        )
        self.assertEqual(expected, result)


def _test(command):
    """Run ``command`` as if it were provided from a user's terminal / CLI.

    Args:
        command (str or list[str]): A raw CLI command to run. e.g. ``"list Sphinx"``.

    Returns:
        list[str]: Captured print text.

    """
    if isinstance(command, six.string_types):
        command = shlex.split(command)

    with mock.patch("rez_dependency._core.streamer.printer") as patch:
        cli.main(command)

    return [call[1][0] for call in patch.mock_calls]
