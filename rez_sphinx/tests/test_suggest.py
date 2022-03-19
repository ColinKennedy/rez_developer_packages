"""Make sure :ref:`rez_sphinx suggest` works as expected."""

import unittest


class Depth(unittest.TestCase):
    """Ensure package traversal order works as expected."""

    def test_depth_check(self):
        """Check packages individually to make sure they have the correct depth."""
        raise ValueError()

    def test_depth_mixed(self):
        """Run a real test, with unittest-friendly Rez packages.

        The most important package is "complex_package", which has 2 dependencies

        - pure_dependency - depth: 0
        - nested_dependency - depth: 3

        Because nested_dependency is 3, "complex_package" needs to be of depth
        3 + 1. This test ensures it has the right value.

        """
        raise ValueError("")


class Invalid(unittest.TestCase):
    """Handle bad cases and either fail or warn the user."""

    def test_path_conflict(self):
        """Fail to run if a source Rez package family is found in more than one place.

        The conflicter checks packages first by UUID and if not found, falls back
        to the package name.

        """
        raise ValueError()

    def test_cyclic(self):
        """Fail / Warn if packages have cyclic dependencies."""
        raise ValueError()


class Options(unittest.TestCase):
    """Check the miscellaneous flags in :ref:`rez_sphinx suggest`."""

    def test_exclude_invalid(self):
        """Non-Python packages should not be included in the output."""
        raise ValueError()

    def test_guess_mode(self):
        """Find Rez dependencies which aren't located in a Package's `requires`_."""
        raise ValueError()

    def test_include_existing(self):
        """Show Rez packages in the output, even if they already have documentation."""
        raise ValueError()

    def test_search_recursive(self):
        """Look for Rez packages recursively, in an unknown folder structure."""
        raise ValueError()
