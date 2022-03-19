"""Make sure :ref:`rez_sphinx suggest` works as expected."""

import functools
import glob
import os
import textwrap
import unittest

from python_compatibility import wrapping
from rez_sphinx.commands.suggest import suggestion_mode
from rez_utilities import finder

from .common import run_test

_CURRENT_DIRECTORY = os.path.dirname(os.path.realpath(__file__))


class _Base(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Getting common directories for testing within this class."""
        super(_Base, cls).setUpClass()

        root = os.path.join(
            _CURRENT_DIRECTORY,
            "data",
            "suggestion_test_nested",
        )
        cls.source_packages = os.path.join(root, "source_packages")
        cls.installed_packages = os.path.join(root, "installed_packages")


class Depth(_Base):
    """Ensure package traversal order works as expected."""

    def test_depth_check(self):
        """Check packages individually to make sure they have the correct depth."""

        def _get_from_packages(packages, name):
            return [package for package in packages if package.name == name][0]

        installed_packages = [
            finder.get_nearest_rez_package(path)
            for path in glob.glob(os.path.join(self.installed_packages, "*", "*"))
        ]

        _get = functools.partial(_get_from_packages, installed_packages)

        another_nested = _get("another_nested")
        complex_package = _get("complex_package")
        nested_dependency = _get("nested_dependency")
        package_plus_pure_dependency = _get("package_plus_pure_dependency")
        pure_dependency = _get("pure_dependency")

        installed_family_names = {package.name: package for package in installed_packages}

        for package, expected in [
            (pure_dependency, 0),
            (package_plus_pure_dependency, 1),
            (another_nested, 2),
            (nested_dependency, 3),
            (complex_package, 4),
        ]:
            found = suggestion_mode._compute_package_depth(package, installed_family_names)

            self.assertEqual(
                expected,
                found,
                msg='Package "{package.name}" expected depth "{expected}" but got '
                'depth "{found}".'.format(package=package, found=found, expected=expected),
            )

    def test_depth_mixed(self):
        """Run a real test, with unittest-friendly Rez packages.

        The most important package is "complex_package", which has 2 dependencies

        - pure_dependency - depth: 0
        - nested_dependency - depth: 3

        Because nested_dependency is 3, "complex_package" needs to be of depth
        3 + 1. This test ensures it has the right value.

        """
        with wrapping.capture_pipes() as (stdout, _):
            run_test.test(
                [
                    "suggest",
                    "build-order",
                    self.source_packages,
                    "--packages-path",
                    self.installed_packages,
                ]
            )

        value = stdout.getvalue()
        stdout.close()

        expected = [
            os.path.join(self.source_packages, name) for name in [
                "pure_dependency",
                "guessable_package",
                "package_plus_pure_dependency",
                "another_nested",
                "nested_dependency",
                "complex_package",
                "second_complex_package",
            ]
        ]

        self.assertEqual(expected, value.splitlines())

    def test_late_bindings(self):
        """Make sure packages with `late()`_ bindings still work."""
        raise ValueError()


class Invalid(unittest.TestCase):
    """Handle bad cases and either fail or warn the user."""

    def test_bad_package_flat(self):
        """Fail early if any directory's package.py is invalid."""
        raise ValueError()

    def test_bad_package_recursive(self):
        """Warn if any directory's package.py is invalid."""
        raise ValueError()

    def test_cyclic(self):
        """Fail if packages have cyclic dependencies."""
        raise ValueError()

    def test_no_resolve(self):
        """Fail early a found package has no resolve equivalent."""
        raise ValueError()

    def test_path_conflict_name(self):
        """Fail to run if a source Rez package family is found in more than one place.

        The conflicter checks packages first by UUID and if not found, falls back
        to the package name.

        """
        raise ValueError()


class Options(_Base):
    """Check the miscellaneous flags in :ref:`rez_sphinx suggest`."""

    def test_allow_cyclic(self):
        """Warn if packages have cyclic dependencies."""
        raise ValueError()

    def test_display_as_names(self):
        """Show the ordered packages like how `rez-depends`_ does."""
        with wrapping.capture_pipes() as (stdout, _):
            run_test.test(
                [
                    "suggest",
                    "build-order",
                    self.source_packages,
                    "--packages-path",
                    self.installed_packages,
                    "--display-as",
                    "names",
                ]
            )

        value = stdout.getvalue()
        stdout.close()

        expected = textwrap.dedent(
            """\
            #0: pure_dependency
            #1: guessable_package package_plus_pure_dependency
            #2: another_nested
            #3: nested_dependency
            #4: complex_package second_complex_package
            """
        )

        self.assertEqual(expected, value)

    def test_exclude_invalid(self):
        """Non-Python packages should not be included in the output."""
        raise ValueError()

    def test_guess_mode(self):
        """Find Rez dependencies which aren't located in a Package's `requires`_."""
        with wrapping.capture_pipes() as (stdout, _):
            run_test.test(
                [
                    "suggest",
                    "build-order",
                    self.source_packages,
                    "--packages-path",
                    self.installed_packages,
                    "--suggestion-mode=guess",
                    "--display-as=names",
                ]
            )

        value = stdout.getvalue()
        stdout.close()

        expected = textwrap.dedent(
            """\
            #0: pure_dependency
            #1: package_plus_pure_dependency
            #2: another_nested
            #3: nested_dependency
            #4: complex_package guessable_package
            #5: second_complex_package
            """
        )

        self.assertEqual(expected, value)

    def test_include_existing(self):
        """Show Rez packages in the output, even if they already have documentation."""
        raise ValueError()

    def test_search_recursive(self):
        """Look for Rez packages recursively, in an unknown folder structure."""
        raise ValueError()
