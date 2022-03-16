"""Make sure the user's `package help`_ features work as expected."""

import contextlib
import os
import textwrap
import unittest

from python_compatibility import wrapping
from rez import developer_package
from rez_utilities import creator, finder
import schema

from rez_sphinx.core import hook
from rez_sphinx.preferences import preference_help

from .common import package_wrap, run_test


class _Base(unittest.TestCase):
    """A quick test class for common methods."""

    def _test(self, expected, help_=None):
        """Create a base Rez package, run :ref:`rez_sphinx` and check ``expected``.

        Args:
            expected (list[list[str, str]]):
                The help entries which should be in the installed package by
                the end of this method.
            help_ (list[list[str, str]] or str or NoneType, optional):
                The initial Rez package `package help`_. If ``None``,
                no ``help`` will be defined. All other input is used as-is.

        """
        # 1. Build the initial Rez package
        package = package_wrap.make_simple_developer_package(help_=help_)
        directory = finder.get_package_root(package)

        # 2. Initialize the documentation
        run_test.test(["init", directory])

        install_path = package_wrap.make_directory("_AppendHelp_test")

        # 3a. Simulate adding the pre-build hook to the user's Rez configuration.
        # 3b. Re-build the Rez package so it can auto-append entries to the package.py ``help``
        #
        with _override_preprocess(package):
            creator.build(package, install_path, quiet=True)

        install_package = developer_package.DeveloperPackage.from_path(
            # `package` is 1.0.0 but we incremented the minor version during
            # :doc:`init_command`. So it's 1.1.0 now.
            #
            os.path.join(install_path, package.name, "1.1.0")
        )

        self.assertEqual(
            expected,
            install_package.help,
            msg='Package "{install_path}" did not match the expected result.'.format(
                install_path=install_path
            ),
        )


class AppendHelp(_Base):
    """Make sure the user's `package help`_ is appended as expected."""

    def test_allow_duplicates(self):
        """Include the user's help labels, if they clash with auto-generated ones."""
        with run_test.keep_config() as config:
            config.optionvars["rez_sphinx"] = dict()
            config.optionvars["rez_sphinx"].setdefault("auto_help", dict())
            config.optionvars["rez_sphinx"]["auto_help"]["filter_by"] = "none"

            self._test(
                [
                    ["Developer Documentation", "developer_documentation.html"],
                    ["Developer Documentation", "foo.html"],
                    ["Home Page", "A help thing"],
                    ["User Documentation", "user_documentation.html"],
                ],
                help_=[
                    ["Developer Documentation", "foo.html"],
                    ["Home Page", "A help thing"],
                ],
            )

    def test_forbid_duplicates_001(self):
        """Remove duplicate auto-generated keys, prefer original keys."""
        with run_test.keep_config() as config:
            config.optionvars["rez_sphinx"] = dict()
            config.optionvars["rez_sphinx"].setdefault("auto_help", dict())
            config.optionvars["rez_sphinx"]["auto_help"][
                "filter_by"
            ] = "prefer_original"

            self._test(
                [
                    ["Developer Documentation", "foo.html"],
                    ["User Documentation", "user_documentation.html"],
                ],
                help_=[
                    ["Developer Documentation", "foo.html"],
                ],
            )

    def test_forbid_duplicates_002(self):
        """Remove duplicate original keys, prefer auto-generated keys."""
        with run_test.keep_config() as config:
            config.optionvars["rez_sphinx"] = dict()
            config.optionvars["rez_sphinx"].setdefault("auto_help", dict())
            config.optionvars["rez_sphinx"]["auto_help"][
                "filter_by"
            ] = "prefer_generated"

            self._test(
                [
                    ["Developer Documentation", "developer_documentation.html"],
                    ["User Documentation", "user_documentation.html"],
                ],
                help_=[
                    ["Developer Documentation", "foo.html"],
                ],
            )

    def test_string(self):
        """Add `package help`_ to a Rez package that has a single string entry."""
        self._test(
            [
                ["Developer Documentation", "developer_documentation.html"],
                ["Home Page", "A help thing"],
                ["User Documentation", "user_documentation.html"],
            ],
            help_="A help thing",
        )

    def test_list_ordered(self):
        """Add `package help`_ to a Rez package that has a list of entries."""
        with run_test.keep_config() as config:
            config.optionvars["rez_sphinx"] = dict()
            config.optionvars["rez_sphinx"].setdefault("auto_help", dict())
            config.optionvars["rez_sphinx"]["auto_help"][
                "sort_order"
            ] = "prefer_original"

            self._test(
                [
                    ["Extra thing", "another"],
                    ["A label", "thing"],
                    ["Developer Documentation", "developer_documentation.html"],
                    ["User Documentation", "user_documentation.html"],
                ],
                help_=[["Extra thing", "another"], ["A label", "thing"]],
            )

    def test_list_sorted(self):
        """Add `package help`_ to a Rez package that has a list of entries."""
        self._test(
            [
                ["A label", "thing"],
                ["Developer Documentation", "developer_documentation.html"],
                ["Extra thing", "another"],
                ["User Documentation", "user_documentation.html"],
            ],
            help_=[["Extra thing", "another"], ["A label", "thing"]],
        )

    def test_none(self):
        """Add `package help`_ to a Rez package that has no defined help."""
        self._test(
            [
                ["Developer Documentation", "developer_documentation.html"],
                ["User Documentation", "user_documentation.html"],
            ],
            help_=None,
        )


class AutoHelpOrder(_Base):
    """Make sure :mod:`rez_sphinx.preferences.preference_help_` functions work."""

    def test_alphabetical(self):
        """Sort all items in ascending, alphabetical order."""
        caller = preference_help.OPTIONS["alphabetical"]

        for original, auto_generated, expected in [
            (
                [["b", "b"], ["z", "z"]],
                [["a", "a"]],
                [["a", "a"], ["b", "b"], ["z", "z"]],
            ),
            (
                [["a", "a"], ["z", "z"]],
                [["b", "b"]],
                [["a", "a"], ["b", "b"], ["z", "z"]],
            ),
            (
                [["a", "a"], ["b", "b"]],
                [["z", "z"]],
                [["a", "a"], ["b", "b"], ["z", "z"]],
            ),
        ]:
            sort = hook._sort(caller, original, original + auto_generated)

            self.assertEqual(expected, sort)

    def test_invalid(self):
        """Stop early if the user's sort option is invalid."""
        # TODO : Add test to ensure invalid order is caught safely
        with run_test.keep_config() as config:
            config.optionvars["rez_sphinx"] = dict()
            config.optionvars["rez_sphinx"].setdefault("auto_help", dict())
            config.optionvars["rez_sphinx"]["auto_help"][
                "sort_order"
            ] = "some_invalid_text"

            self._test(
                [
                    ["Extra thing", "another"],
                    ["A label", "thing"],
                    ["Developer Documentation", "developer_documentation.html"],
                    ["User Documentation", "user_documentation.html"],
                ],
                help_=[["Extra thing", "another"], ["A label", "thing"]],
            )

    def test_sort_prefer_generated(self):
        """Sort auto-generated help before anything the user defined."""
        caller = preference_help.OPTIONS["prefer_generated"]

        for original, auto_generated, expected in [
            (
                [["z", "z"], ["a", "a"]],
                [["t", "t"], ["b", "b"]],
                [["b", "b"], ["t", "t"], ["z", "z"], ["a", "a"]],
            ),
        ]:
            sort = hook._sort(caller, original, original + auto_generated)

            self.assertEqual(expected, sort)

    def test_sort_prefer_original(self):
        """Sort hand-written help before anything the auto-generated."""
        caller = preference_help.OPTIONS["prefer_original"]

        for original, auto_generated, expected in [
            (
                [["z", "z"], ["a", "a"]],
                [["t", "t"], ["b", "b"]],
                [["z", "z"], ["a", "a"], ["b", "b"], ["t", "t"]],
            ),
        ]:
            sort = hook._sort(caller, original, original + auto_generated)

            self.assertEqual(expected, sort)


class HelpScenarios(unittest.TestCase):
    """Make sure the all automation revolving `package help`_ works."""

    def test_do_nothing(self):
        """Don't change the user's `package help`_ if there's no documentation."""
        # 1. Build the initial Rez package
        package = package_wrap.make_simple_developer_package()
        directory = finder.get_package_root(package)

        # 2. Initialize the documentation
        run_test.test(["init", directory])

        # 2b. Remove the files for the sake of this unittest
        documentation_root = os.path.join(directory, "documentation", "source")

        os.remove(os.path.join(documentation_root, "developer_documentation.rst"))
        os.remove(os.path.join(documentation_root, "user_documentation.rst"))

        # 3. Add a rez_sphinx over a Sphinx ref role.
        _add_example_ref_role(os.path.join(directory, "documentation", "source"))

        install_path = package_wrap.make_directory("_test_ref_role")

        # 4a. Simulate adding the pre-build hook to the user's Rez configuration.
        # 4b. Re-build the Rez package so it can auto-append entries to the package.py ``help``
        #
        with _override_preprocess(package):
            creator.build(package, install_path, quiet=True)

        install_package = developer_package.DeveloperPackage.from_path(
            # `package` is 1.0.0 but we incremented the minor version during
            # :doc:`init_command`. So it's 1.1.0 now.
            #
            os.path.join(install_path, package.name, "1.1.0")
        )

        expected = [["Some Tag", "some_page.html#some-example-ref"]]

        self.assertEqual(
            expected,
            install_package.help,
            msg='Package "{install_path}" did not match the expected result.'.format(
                install_path=install_path
            ),
        )

    def test_escaped_colon(self):
        """Make sure a documentation label containing a separator still works."""
        # - When converting "Tagged" Sphinx .rst files, add a unittest to make sure ":" is escapable. Since ":" is also the delimiter
        raise ValueError()

    def test_ref_role(self):
        """Use a custom Sphinx reference if the user explicitly added one."""
        # 1. Build the initial Rez package
        package = package_wrap.make_simple_developer_package()
        directory = finder.get_package_root(package)

        # 2. Initialize the documentation
        run_test.test(["init", directory])

        # 3. Add a rez_sphinx over a Sphinx ref role.
        _add_example_ref_role(os.path.join(directory, "documentation", "source"))

        install_path = package_wrap.make_directory("_test_ref_role")

        # 4a. Simulate adding the pre-build hook to the user's Rez configuration.
        # 4b. Re-build the Rez package so it can auto-append entries to the package.py ``help``
        #
        with _override_preprocess(package):
            creator.build(package, install_path, quiet=True)

        install_package = developer_package.DeveloperPackage.from_path(
            # `package` is 1.0.0 but we incremented the minor version during
            # :doc:`init_command`. So it's 1.1.0 now.
            #
            os.path.join(install_path, package.name, "1.1.0")
        )

        expected = [
            ["Developer Documentation", "developer_documentation.html"],
            ["Some Tag", "some_page.html#some-example-ref"],
            ["User Documentation", "user_documentation.html"],
        ]

        self.assertEqual(
            expected,
            install_package.help,
            msg='Package "{install_path}" did not match the expected result.'.format(
                install_path=install_path
            ),
        )


def _add_example_ref_role(root):
    """Add a quick rez_sphinx_help tag above some Sphinx header.

    Args:
        root (str): The top-level documentation folder. e.g. "{root}/documentation/source".

    """
    with open(os.path.join(root, "some_page.rst"), "w") as handler:
        handler.write(
            textwrap.dedent(
                """\
                Some header
                ===========

                ..
                    rez_sphinx_help:Some Tag

                .. _some example ref:

                An inner header
                ---------------

                Some text
                """
            )
        )


@contextlib.contextmanager
def _override_preprocess(package):
    """Pretend the user has a "proper" :ref:`rez_sphinx` environment set up.

    In this case "proper" means:

    - They're cd'ed into the Rez package
    - Their `package_preprocess_function`_ is set properly so that
      `package help`_ is auto-generated.
    - Any other environment related details.

    Args:
        package (:class:`rez.developer_package.DeveloperPackage`):
            Some developer (source) Rez package to cd into.

    Yields:
        context: A "proper" environment for :ref:`rez_sphinx`.

    """
    with wrapping.keep_cwd(), run_test.keep_config() as config:
        # Simulate the user CDing into a developer Rez package, just before
        # build / release / test.
        #
        root = finder.get_package_root(package)
        os.chdir(root)

        config.package_preprocess_function = hook.package_preprocess_function

        yield
