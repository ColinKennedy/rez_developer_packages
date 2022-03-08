"""Make sure the user's :ref:`package help` features work as expected."""

import contextlib
import os
import unittest

from rez import developer_package
from python_compatibility import wrapping
from rez_utilities import creator, finder
from rez_sphinx.core import hook

from .common import package_wrap, run_test


class AppendHelp(unittest.TestCase):
    """Make sure the user's :ref:`package help` is appended as expected."""

    def _test(self, expected, help_=None):
        """Create a base Rez package, run :ref:`rez_sphinx` and check ``expected``.

        Args:
            expected (list[list[str, str]]):
                The help entries which should be in the installed package by
                the end of this method.
            help_ (list[list[str, str]] or str or NoneType, optional):
                The initial Rez package :ref:`package help`. If ``None``,
                no ``help`` will be defined. All other input is used as-is.

        """
        # 1. Build the initial Rez package
        package = package_wrap.make_simple_developer_package(help_=help_)
        directory = finder.get_package_root(package)

        # 2. Initialize the documentation
        run_test.test(["init", directory])

        install_path = package_wrap.make_directory("_AppendHelp_test_none")

        # 3a. Simulate adding the pre-build hook to the user's Rez configuration.
        # 3b. Re-build the Rez package so it can auto-append entries to the package.py ``help``
        #
        with _override_preprocess(package):
            creator.build(package, install_path, quiet=True)

        install_package = developer_package.DeveloperPackage.from_path(
            # `package` is 1.0.0 but we incremented the minor version during
            # :ref:`rez_sphinx init`. So it's 1.1.0 now.
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

    def test_string(self):
        """Add :ref:`package help` to a Rez package that has a single string entry."""
        self._test(
            [],
            help_=["A help thing"],
        )

    def test_list_ordered(self):
        """Add :ref:`package help` to a Rez package that has a list of entries."""
        self._test(
            [
                ["Extra thing", "another"],
                ["A label", "thing"],
                ['Developer Documentation', 'developer_documentation.html'],
                ['User Documentation', 'user_documentation.html']
            ],
            help_=[["Extra thing", "another"], ["A label", "thing"]],
        )

    def test_list_sorted(self):
        """Add :ref:`package help` to a Rez package that has a list of entries."""
        self._test(
            [
                ["A label", "thing"],
                ['Developer Documentation', 'developer_documentation.html'],
                ["Extra thing", "another"],
                ['User Documentation', 'user_documentation.html']
            ],
            help_=[["Extra thing", "another"], ["A label", "thing"]],
        )

    def test_none(self):
        """Add :ref:`package help` to a Rez package that has no defined help."""
        self._test(
            [
                ['Developer Documentation', 'developer_documentation.html'],
                ['User Documentation', 'user_documentation.html']
            ],
            help_=None,
        )


class HelpScenarios(unittest.TestCase):
    """Make sure the all automation revolving :ref:`package help` works."""

    def test_do_nothing(self):
        """Don't change the user's :ref:`package help` if there's no documentation."""
        raise ValueError()

    def test_escaped_colon(self):
        """Make sure a documentation label containing a separator still works."""
        # - When converting "Tagged" Sphinx .rst files, add a unittest to make sure ":" is escapable. Since ":" is also the delimiter
        raise ValueError()

    def test_ref_role(self):
        """Use a custom Sphinx reference if the user explicitly added one."""
        ".. _foo:"
        # - If the .. rez_sphinx comment (tag) is above a sphinx ref like .. _foo::, include that anchor in the text when it gets added to rez-help
        raise ValueError()


@contextlib.contextmanager
def _override_preprocess(package):
    """Pretend the user has a "proper" :ref:`rez_sphinx` environment set up.

    In this case "proper" means:

    - They're cd'ed into the Rez package
    - Their :ref:`package_preprocess_function` is set properly so that
      :ref:`package help` is auto-generated.
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