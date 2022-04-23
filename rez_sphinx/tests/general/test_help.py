"""Make sure the user's `package help`_ features work as expected."""

import atexit
import contextlib
import functools
import io
import os
import tempfile
import textwrap
import unittest

from python_compatibility import wrapping
from rez import developer_package
from rez_utilities import creator, finder
from six.moves import mock

from rez_sphinx.core import exception, generic
from rez_sphinx.preferences import preference_help
from rez_sphinx.preprocess import hook, preprocess_entry_point

from ..common import package_wrap, run_test

_CURRENT_DIRECTORY = os.path.dirname(os.path.realpath(__file__))
_PACKAGE_ROOT = os.path.dirname(os.path.dirname(_CURRENT_DIRECTORY))


class _Base(unittest.TestCase):
    """A quick test class for common methods."""

    def _test(self, expected, help_=None):
        """Create a base Rez package, run :ref:`rez_sphinx` and check ``expected``.

        Args:
            expected (list[list[str, str]]):
                The help entries which should be in the installed package by
                the end of this method.
            help_ (list[list[str, str]] or str or None, optional):
                The initial Rez package `package help`_. If ``None``,
                no ``help`` will be defined. All other input is used as-is.

        """
        # 1. Build the initial Rez package
        package = package_wrap.make_simple_developer_package(help_=help_)
        directory = finder.get_package_root(package)

        # 2. Initialize the documentation
        run_test.test(["init", directory])

        # 3a. Simulate adding the pre-build hook to the user's Rez configuration.
        # 4b. Re-build the Rez package and auto-append entries to the `help`_.
        #
        with _override_preprocess(package), mock.patch(
            "rez_sphinx.core.environment.is_publishing_enabled"
        ) as is_publishing_enabled:
            is_publishing_enabled.return_value = False
            full_help = hook.preprocess_help(directory, package.help)

        self.assertEqual(expected, full_help)


class AppendHelp(_Base):
    """Make sure the user's `package help`_ is appended as expected."""

    def test_allow_duplicates(self):
        """Include the user's help labels, if they clash with auto-generated ones."""
        with run_test.keep_config() as config:
            config.optionvars["rez_sphinx"] = {"auto_help": {"filter_by": "none"}}

            self._test(
                [
                    ["Developer Documentation", "foo.html"],
                    ["Developer Documentation", "{root}/developer_documentation.html"],
                    ["Home Page", "A help thing"],
                    ["User Documentation", "{root}/user_documentation.html"],
                    ["rez_sphinx objects.inv", "{root}"],
                ],
                help_=[
                    ["Developer Documentation", "foo.html"],
                    ["Home Page", "A help thing"],
                ],
            )

    def test_forbid_duplicates_001(self):
        """Remove duplicate auto-generated keys, prefer original keys."""
        join = os.path.join

        with run_test.keep_config() as config:
            config.optionvars["rez_sphinx"] = {
                "auto_help": {"filter_by": "prefer_original"},
            }

            self._test(
                [
                    ["Developer Documentation", "foo.html"],
                    ["User Documentation", join("{root}", "user_documentation.html")],
                    ["rez_sphinx objects.inv", "{root}"],
                ],
                help_=[
                    ["Developer Documentation", "foo.html"],
                ],
            )

    def test_forbid_duplicates_002(self):
        """Remove duplicate original keys, prefer auto-generated keys."""
        with run_test.keep_config() as config:
            config.optionvars["rez_sphinx"] = {
                "auto_help": {
                    "filter_by": "prefer_generated",
                },
            }

            self._test(
                [
                    [
                        "Developer Documentation",
                        os.path.join("{root}", "developer_documentation.html"),
                    ],
                    [
                        "User Documentation",
                        os.path.join("{root}", "user_documentation.html"),
                    ],
                    ["rez_sphinx objects.inv", "{root}"],
                ],
                help_=[
                    ["Developer Documentation", "foo.html"],
                ],
            )

    def test_list_ordered(self):
        """Add `package help`_ to a Rez package that has a list of entries."""
        with run_test.keep_config() as config:
            config.optionvars = {
                "rez_sphinx": {"auto_help": {"sort_order": "prefer_original"}},
            }

            self._test(
                [
                    ["Extra thing", "another"],
                    ["A label", "thing"],
                    [
                        "Developer Documentation",
                        "{root}/developer_documentation.html",
                    ],
                    [
                        "User Documentation",
                        "{root}/user_documentation.html",
                    ],
                    ["rez_sphinx objects.inv", "{root}"],
                ],
                help_=[["Extra thing", "another"], ["A label", "thing"]],
            )

    def test_list_sorted(self):
        """Add `package help`_ to a Rez package that has a list of entries."""
        self._test(
            [
                ["A label", "thing"],
                [
                    "Developer Documentation",
                    os.path.join("{root}", "developer_documentation.html"),
                ],
                ["Extra thing", "another"],
                [
                    "User Documentation",
                    os.path.join("{root}", "user_documentation.html"),
                ],
                ["rez_sphinx objects.inv", "{root}"],
            ],
            help_=[["Extra thing", "another"], ["A label", "thing"]],
        )

    def test_none(self):
        """Add `package help`_ to a Rez package that has no defined help."""
        self._test(
            [
                [
                    "Developer Documentation",
                    "{root}/developer_documentation.html",
                ],
                [
                    "User Documentation",
                    "{root}/user_documentation.html",
                ],
                [
                    "rez_sphinx objects.inv",
                    "{root}",
                ],
            ],
            help_=None,
        )

    def test_string(self):
        """Add `package help`_ to a Rez package that has a single string entry."""
        self._test(
            [
                [
                    "Developer Documentation",
                    "{root}/developer_documentation.html",
                ],
                ["Home Page", "A help thing"],
                [
                    "User Documentation",
                    "{root}/user_documentation.html",
                ],
                ["rez_sphinx objects.inv", "{root}"],
            ],
            help_="A help thing",
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
            sort = hook._sort(  # pylint: disable=protected-access
                caller,
                original,
                original + auto_generated,
            )

            self.assertEqual(expected, sort)

    def test_invalid(self):
        """Stop early if the user's sort option is invalid."""
        with run_test.keep_config() as config:
            config.optionvars["rez_sphinx"] = {
                "auto_help": {"sort_order": "some_invalid_text"},
            }

            with self.assertRaises(exception.ConfigurationError):
                self._test([])

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
            sort = hook._sort(  # pylint: disable=protected-access
                caller,
                original,
                original + auto_generated,
            )

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
            sort = hook._sort(  # pylint: disable=protected-access
                caller,
                original,
                original + auto_generated,
            )

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
        documentation_root = os.path.join(directory, "documentation")

        os.remove(os.path.join(documentation_root, "developer_documentation.rst"))
        os.remove(os.path.join(documentation_root, "user_documentation.rst"))

        # 3. Add a rez_sphinx over a Sphinx ref role.
        _add_example_ref_role(os.path.join(directory, "documentation"))

        with _override_preprocess(package), mock.patch(
            "rez_sphinx.core.environment.is_publishing_enabled"
        ) as is_publishing_enabled:
            is_publishing_enabled.return_value = False
            full_help = hook.preprocess_help(directory, package.help)

        expected = [
            ["Some Tag", "{root}/some_page.html#an-inner-header"],
            ["rez_sphinx objects.inv", "{root}"],
        ]

        self.assertEqual(expected, full_help)

    def test_ref_role_header_not_found(self):
        """Handle `package help`_ when a :ref:`rez_sphinx_help` tag has no destination.

        For example, if a user has documentation like this

        ::

            ..
                rez_sphinx_help:Some Tag

            thing

            Header Here
            ===========

        Then we should **not** auto-attach ``"Header Here"`` as an anchor like
        ``"#header-here.html"``.  Instead, leave the destination blank.

        """
        # 1. Build the initial Rez package
        package = package_wrap.make_simple_developer_package()
        directory = finder.get_package_root(package)

        # 2. Initialize the documentation
        run_test.test(["init", directory])

        # 3. Add a rez_sphinx over a Sphinx ref role.
        _add_example_ref_role(
            os.path.join(directory, "documentation"),
            textwrap.dedent(
                """\
                ==========
                Top Header
                ==========

                Text here

                ..
                    rez_sphinx_help:Some Tag

                thing

                Header Here
                ===========
                """
            ),
        )

        # 3a. Simulate adding the pre-build hook to the user's Rez configuration.
        # 4b. Re-build the Rez package and auto-append entries to the `help`_.
        #
        with _override_preprocess(package), mock.patch(
            "rez_sphinx.core.environment.is_publishing_enabled"
        ) as is_publishing_enabled:
            is_publishing_enabled.return_value = False
            full_help = hook.preprocess_help(directory, package.help)

        expected = [
            ["Developer Documentation", "{root}/developer_documentation.html"],
            ["Some Tag", "{root}/some_page.html"],
            ["User Documentation", "{root}/user_documentation.html"],
            ["rez_sphinx objects.inv", "{root}"],
        ]

        self.assertEqual(expected, full_help)

    def test_ref_role_use_top_header_001(self):
        """Get the Sphinx top header and use that as a Rez `help`_ entry."""
        # 1. Build the initial Rez package
        package = package_wrap.make_simple_developer_package()
        directory = finder.get_package_root(package)

        # 2. Initialize the documentation
        run_test.test(["init", directory])

        # 3. Add a rez_sphinx over a Sphinx ref role.
        _add_example_ref_role(
            os.path.join(directory, "documentation"),
            textwrap.dedent(
                """\
                ==========
                Top Header
                ==========

                Text here

                ..
                    rez_sphinx_help

                thing

                Header Here
                ===========
                """
            ),
        )

        # 3a. Simulate adding the pre-build hook to the user's Rez configuration.
        # 4b. Re-build the Rez package and auto-append entries to the `help`_.
        #
        with _override_preprocess(package), mock.patch(
            "rez_sphinx.core.environment.is_publishing_enabled"
        ) as is_publishing_enabled:
            is_publishing_enabled.return_value = False
            full_help = hook.preprocess_help(directory, package.help)

        expected = [
            ["Developer Documentation", "{root}/developer_documentation.html"],
            ["Top Header", "{root}/some_page.html"],
            ["User Documentation", "{root}/user_documentation.html"],
            ["rez_sphinx objects.inv", "{root}"],
        ]

        self.assertEqual(expected, full_help)

    def test_ref_role_use_top_header_002(self):
        """Use the Sphinx file name as a Rez `help`_ entry."""
        # 1. Build the initial Rez package
        package = package_wrap.make_simple_developer_package()
        directory = finder.get_package_root(package)

        # 2. Initialize the documentation
        run_test.test(["init", directory])

        # 3. Add a rez_sphinx over a Sphinx ref role.
        _add_example_ref_role(
            os.path.join(directory, "documentation"),
            textwrap.dedent(
                """\
                Text here

                ..
                    rez_sphinx_help

                thing

                Header Here
                ===========
                """
            ),
        )

        # 3a. Simulate adding the pre-build hook to the user's Rez configuration.
        # 4b. Re-build the Rez package and auto-append entries to the `help`_.
        #
        with _override_preprocess(package), mock.patch(
            "rez_sphinx.core.environment.is_publishing_enabled"
        ) as is_publishing_enabled:
            is_publishing_enabled.return_value = False
            full_help = hook.preprocess_help(directory, package.help)

        expected = [
            ["Developer Documentation", "{root}/developer_documentation.html"],
            ["Some Page", "{root}/some_page.html"],
            ["User Documentation", "{root}/user_documentation.html"],
            ["rez_sphinx objects.inv", "{root}"],
        ]

        self.assertEqual(expected, full_help)

    def test_ref_role(self):
        """Use a custom Sphinx reference if the user explicitly added one."""
        # 1. Build the initial Rez package
        package = package_wrap.make_simple_developer_package()
        directory = finder.get_package_root(package)

        # 2. Initialize the documentation
        run_test.test(["init", directory])

        # 3. Add a rez_sphinx over a Sphinx ref role.
        _add_example_ref_role(os.path.join(directory, "documentation"))

        with _override_preprocess(package), mock.patch(
            "rez_sphinx.core.environment.is_publishing_enabled"
        ) as is_publishing_enabled:
            is_publishing_enabled.return_value = False
            full_help = hook.preprocess_help(directory, package.help)

        expected = [
            [
                "Developer Documentation",
                os.path.join("{root}", "developer_documentation.html"),
            ],
            [
                "Some Tag",
                os.path.join("{root}", "some_page.html#an-inner-header"),
            ],
            [
                "User Documentation",
                os.path.join("{root}", "user_documentation.html"),
            ],
            [
                "rez_sphinx objects.inv",
                "{root}",
            ],
        ]

        self.assertEqual(expected, full_help)


def _add_example_ref_role(root, text=""):
    """Add a quick rez_sphinx_help tag above some Sphinx header.

    Args:
        root (str):
            The top-level documentation folder. e.g. "{root}/documentation/source".
        text (str, optional):
            A .rst file contents to use for this function.

    """
    text = text or textwrap.dedent(
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

    with io.open(os.path.join(root, "some_page.rst"), "w", encoding="utf-8") as handler:
        handler.write(generic.decode(text))


def _make_configuration_file(text):
    """Make a `rezconfig.py`_, using ``text``."""
    _, path = tempfile.mkstemp(suffix="_make_configuration_file")
    atexit.register(functools.partial(os.remove, path))

    with io.open(path, "w", encoding="utf-8") as handler:
        handler.write(textwrap.dedent(text))

    return path


@contextlib.contextmanager
def _override_preprocess(package):
    """Pretend the user has a "proper" :ref:`rez_sphinx` environment set up.

    In this case "proper" means:

    - They're cd'ed into the Rez package
    - Their `package_preprocess_function`_ is set properly so that
      `package help`_ is auto-generated.
    - Any other environment related details.

    Args:
        package (rez.packages.Package): Some developer (source) Rez package to cd into.

    Yields:
        context: A "proper" environment for :ref:`rez_sphinx`.

    """
    template = textwrap.dedent(
        """
        optionvars = {
            "rez_docbot": {
                "publishers": [
                    {
                        "authentication": [
                            {"user": "foo", "token": "bar", "type": "github"},
                        ],
                        "repository_uri": "git@blah:FooBar/thing",
                        "view_url": "some.website",
                    },
                ],
            }
        }
        package_definition_build_python_paths = %s
        package_preprocess_function = "preprocess_entry_point.run"
        """
    )

    build_paths = [os.path.join(_PACKAGE_ROOT, "python", "rez_sphinx", "preprocess")]
    path = package_wrap.make_rez_configuration(template % build_paths)

    with wrapping.keep_cwd(), wrapping.keep_os_environment(), run_test.keep_config() as config:
        os.environ["REZ_CONFIG_FILE"] = path

        # Simulate the user CDing into a developer Rez package, just before
        # build / release / test.
        #
        root = finder.get_package_root(package)
        os.chdir(root)

        config.package_definition_build_python_paths = build_paths
        config.package_preprocess_function = "preprocess_entry_point.run"

        yield
