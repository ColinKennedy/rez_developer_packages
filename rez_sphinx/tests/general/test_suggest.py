"""Make sure :ref:`rez_sphinx suggest` works as expected."""

import functools
import glob
import os
import textwrap
import unittest

from python_compatibility import wrapping
from rez_utilities import finder

from rez_sphinx.commands.suggest import suggestion_mode
from rez_sphinx.core import exception

from ..common import run_test

_CURRENT_DIRECTORY = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
_PACKAGE_ROOT = os.path.dirname(_CURRENT_DIRECTORY)


class _Base(unittest.TestCase):
    """A common class to make dealing with unittests in this module easier."""

    @classmethod
    def setUpClass(cls):
        """Store common directories for testing within this class."""
        super(_Base, cls).setUpClass()

        root = os.path.join(_PACKAGE_ROOT, "_test_data", "suggestion_test_nested")
        cls.source_packages = os.path.join(root, "source_packages")


class Depth(_Base):
    """Ensure package traversal order works as expected."""

    def test_depth_check(self):
        """Check packages individually to make sure they have the correct depth."""

        def _get_from_packages(packages, name):
            return [package for package in packages if package.name == name][0]

        source_packages = [
            finder.get_nearest_rez_package(path)
            for path in glob.glob(os.path.join(self.source_packages, "*"))
        ]

        _get = functools.partial(_get_from_packages, source_packages)

        another_nested = _get("another_nested")
        complex_package = _get("complex_package")
        nested_dependency = _get("nested_dependency")
        package_plus_pure_dependency = _get("package_plus_pure_dependency")
        pure_dependency = _get("pure_dependency")

        installed_family_names = {package.name: package for package in source_packages}

        for package, expected in [
            (pure_dependency, 0),
            (package_plus_pure_dependency, 1),
            (another_nested, 2),
            (nested_dependency, 3),
            (complex_package, 4),
        ]:
            found = suggestion_mode._compute_package_depth(  # pylint: disable=protected-access,line-too-long
                package,
                installed_family_names,
            )

            self.assertEqual(
                expected,
                found,
                msg='Package "{package.name}" expected depth "{expected}" but got '
                'depth "{found}".'.format(
                    package=package, found=found, expected=expected
                ),
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
            run_test.test(["suggest", "build-order", self.source_packages])

        value = stdout.getvalue()
        stdout.close()

        expected = [
            os.path.join(self.source_packages, name)
            for name in [
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

    def test_early_bindings(self):
        """Make sure packages with `early()`_ bindings still work."""
        root = os.path.join(_PACKAGE_ROOT, "_test_data", "early_binding")
        source_packages = os.path.join(root, "source_packages")

        with wrapping.capture_pipes() as (stdout, _):
            run_test.test(
                ["suggest", "build-order", source_packages, "--display-as=names"]
            )

        value = stdout.getvalue()
        stdout.close()

        self.assertEqual(
            textwrap.dedent(
                """\
                #0: dependency
                #1: early_package
                """
            ),
            value,
        )

    def test_late_bindings(self):
        """Make sure packages with `late()`_ bindings still work."""
        root = os.path.join(_PACKAGE_ROOT, "_test_data", "late_binding")
        source_packages = os.path.join(root, "source_packages")

        with wrapping.capture_pipes() as (stdout, _):
            run_test.test(
                ["suggest", "build-order", source_packages, "--display-as=names"]
            )

        value = stdout.getvalue()
        stdout.close()

        self.assertEqual(
            textwrap.dedent(
                """\
                #0: dependency
                #1: late_package
                """
            ),
            value,
        )


class Invalid(unittest.TestCase):
    """Handle bad cases and either fail or warn the user."""

    def test_bad_package_flat(self):
        """Fail early if any directory's package.py is invalid."""
        root = os.path.join(_PACKAGE_ROOT, "_test_data", "bad_package")
        source_packages = os.path.join(root, "source_packages")

        with self.assertRaises(exception.BadPackage):
            run_test.test(["suggest", "build-order", source_packages])

    def test_bad_package_recursive(self):  # pylint: disable=no-self-use
        """Warn if any directory's package.py is invalid."""
        root = os.path.join(_PACKAGE_ROOT, "_test_data", "bad_package")
        source_packages = os.path.join(root, "source_packages")

        run_test.test(
            ["suggest", "build-order", source_packages, "--search-mode=recursive"]
        )

    def test_path_conflict_name(self):
        """Fail to run if a source Rez package family is found in more than one place.

        The conflicter checks packages first by UUID and if not found, falls back
        to the package name.

        """
        root = os.path.join(_PACKAGE_ROOT, "_test_data", "conflicting_names")
        source_1 = os.path.join(root, "source_1")
        source_2 = os.path.join(root, "source_2")

        with self.assertRaises(exception.PackageConflict):
            run_test.test(["suggest", "build-order", source_1, source_2])


class Options(_Base):
    """Check the miscellaneous flags in :ref:`rez_sphinx suggest`."""

    def test_allow_cyclic(self):
        """Warn if packages have cyclic dependencies."""
        root = os.path.join(_PACKAGE_ROOT, "_test_data", "cyclic_dependencies")
        source_packages = os.path.join(root, "source_packages")

        with wrapping.capture_pipes() as (stdout, _):
            run_test.test(
                ["suggest", "build-order", source_packages, "--display-as=names"]
            )

        value = stdout.getvalue()
        stdout.close()

        self.assertEqual("#0: a_package another_package", value.rstrip())

    def test_display_as_names(self):
        """Show the ordered packages like how `rez-depends`_ does."""
        with wrapping.capture_pipes() as (stdout, _):
            run_test.test(
                [
                    "suggest",
                    "build-order",
                    self.source_packages,
                    "--display-as=names",
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

    def test_guess_mode(self):
        """Find Rez dependencies which aren't located in a Package's `requires`_."""
        with wrapping.capture_pipes() as (stdout, _):
            run_test.test(
                [
                    "suggest",
                    "build-order",
                    self.source_packages,
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

    def test_filter_by_already_released(self):
        """Filter out packages whose documentation are released.

        Do not filter out un-released packages, even if they already have
        documentation.

        """
        raise ValueError()

    def test_filter_by_already_released(self):
        raise ValueError()
        raise ValueError('Do this one')
        root = os.path.join(_PACKAGE_ROOT, "_test_data", "existing_documentation")
        source_packages = os.path.join(root, "source_packages")

        with wrapping.capture_pipes() as (stdout, _):
            run_test.test(
                [
                    "suggest",
                    "build-order",
                    source_packages,
                    "--display-as=names",
                    "--filter-by=none",
                ]
            )

        include_existing_value = stdout.getvalue()
        stdout.close()

        with wrapping.capture_pipes() as (stdout, _):
            run_test.test(
                [
                    "suggest",
                    "build-order",
                    source_packages,
                    "--display-as=names",
                ]
            )

        normal_value = stdout.getvalue()
        stdout.close()

        expected_normal = "#0: no_documentation"
        expected_include_existing = "#0: has_documentation no_documentation"

        self.assertEqual(expected_normal, normal_value.rstrip())
        self.assertEqual(expected_include_existing, include_existing_value.rstrip())

    def test_include_existing(self):
        """Show Rez packages in the output, even if they already have documentation."""
        raise ValueError('Do this one')
        root = os.path.join(_PACKAGE_ROOT, "_test_data", "existing_documentation")
        source_packages = os.path.join(root, "source_packages")

        with wrapping.capture_pipes() as (stdout, _):
            run_test.test(
                [
                    "suggest",
                    "build-order",
                    source_packages,
                    "--display-as=names",
                    "--filter-by=none",
                ]
            )

        include_existing_value = stdout.getvalue()
        stdout.close()

        with wrapping.capture_pipes() as (stdout, _):
            run_test.test(
                [
                    "suggest",
                    "build-order",
                    source_packages,
                    "--display-as=names",
                ]
            )

        normal_value = stdout.getvalue()
        stdout.close()

        expected_normal = "#0: no_documentation"
        expected_include_existing = "#0: has_documentation no_documentation"

        self.assertEqual(expected_normal, normal_value.rstrip())
        self.assertEqual(expected_include_existing, include_existing_value.rstrip())

    def test_search_recursive(self):
        """Look for Rez packages recursively, in an unknown folder structure."""
        root = os.path.join(_PACKAGE_ROOT, "_test_data", "unknown_folder_structure")
        source_packages = os.path.join(root, "source_packages")

        with wrapping.capture_pipes() as (stdout, _):
            run_test.test(
                [
                    "suggest",
                    "build-order",
                    source_packages,
                    "--search-mode=recursive",
                    "--display-as=names",
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
