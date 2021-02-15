#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""A series of tests for modifying a Rez package's conf.py file."""

import sys
import tempfile
import textwrap

from python_compatibility.sphinx import exceptions
from rez_documentation_check.core import sphinx_helper

from . import common


_PYTHON_2 = sys.version_info.major == 2


class _Tester(common.Common):
    """A common tester class that keeps track of temporary files so they are auto-removed."""

    def _test(self, expected, links, code):
        """Create a test file containing `code` and try to change the file into `expected`.

        Args:
            expected (str): The conf.py that should be generated once the unittest completes.
            links (dict[str, str or tuple[str, str or NoneType]]): The Rez package
                + URL link that is being added to `code`.
            code (str): The input conf.py file that needs to be changed into `expected`.

        """
        with tempfile.NamedTemporaryFile(
            suffix=".py", mode="w", delete=False
        ) as handler:
            handler.write(code)

        self.delete_item_later(handler.name)
        sphinx_helper.replace_intersphinx_mapping(links, handler.name)

        with open(handler.name, "r") as sphinx_file:
            output = sphinx_file.read()

        self.assertEqual(expected, output)


class Append(_Tester):
    """Add ``intersphinx_mapping`` to conf.py files that don't already have it."""

    def test_empty(self):
        """Add an intersphinx mapping if the conf.py is empty."""
        code = ""
        links = {"some_package": ("https://google.com", None)}

        if _PYTHON_2:
            expected = "intersphinx_mapping = {   'some_package': ('https://google.com', None)}\n"
        else:
            expected = (
                "intersphinx_mapping = {'some_package': ('https://google.com', None)}\n"
            )

        self._test(expected, links, code)

    def test_missing(self):
        """Add an intersphinx mapping if the conf.py has text but has no mapping."""
        code = textwrap.dedent(
            """\
            project = "foo"

            release = version = '1.0.0'"""
        )
        links = {"some_package": ("https://google.com", None)}
        if _PYTHON_2:
            expected = textwrap.dedent(
                """\
                project = "foo"

                release = version = '1.0.0'
                intersphinx_mapping = {   'some_package': ('https://google.com', None)}
                """
            )
        else:
            expected = textwrap.dedent(
                """\
                project = "foo"

                release = version = '1.0.0'
                intersphinx_mapping = {'some_package': ('https://google.com', None)}
                """
            )

        self._test(expected, links, code)


class Special(_Tester):
    """A series of unlikely unittests that still need to be considered by the replacer."""

    def test_fix(self):
        """Replace an invalid mapping with a valid one."""
        code = textwrap.dedent(
            """\
            project = "foo"

            release = version = "1.0.0"

            intersphinx_mapping = []  # This should not be a list, but a dict
            """
        )
        links = {"some_package": ("https://google.com", None)}
        expected = textwrap.dedent(
            """\
            project = "foo"

            release = version = "1.0.0"

            intersphinx_mapping = {
                "some_package": ('https://google.com', None),
            }  # This should not be a list, but a dict
            """
        )
        self._test(expected, links, code)

    def test_unpack(self):
        """Check that doing multi-variable assignment still replaces correctly."""
        code = textwrap.dedent(
            """\
            project = "foo"

            release = version = "1.0.0"

            foo, intersphinx_mapping, bar = [None, dict(), None]
            """
        )
        links = {"some_package": ("https://google.com", None)}
        expected = textwrap.dedent(
            """\
            project = "foo"

            release = version = "1.0.0"

            foo, intersphinx_mapping, bar = {
                "some_package": ('https://google.com', None),
            }
            """
        )
        self._test(expected, links, code)

    def test_chained_assignment(self):
        """Check that doing multi-variable assignment still replaces correctly."""
        code = textwrap.dedent(
            """\
            project = "foo"

            release = version = "1.0.0"

            foo = intersphinx_mapping = bar = dict()
            """
        )
        links = {"some_package": ("https://google.com", None)}
        expected = textwrap.dedent(
            """\
            project = "foo"

            release = version = "1.0.0"

            foo = intersphinx_mapping = bar = {
                "some_package": ('https://google.com', None),
            }
            """
        )
        self._test(expected, links, code)

    def test_overwrite(self):
        """Remove an existing key/value with a new key/value pair."""
        code = textwrap.dedent(
            """\
            project = "foo"

            release = version = "1.0.0"

            intersphinx_mapping = {
                "existing": "value",
                "another": "asdfasdf",
            }
            """
        )
        links = {"another": ("https://google.com", None), "existing": "value"}
        expected = textwrap.dedent(
            """\
            project = "foo"

            release = version = "1.0.0"

            intersphinx_mapping = {
                "another": ('https://google.com', None),
                "existing": "value",
            }
            """
        )
        self._test(expected, links, code)

    def test_overwrite_single_001(self):
        """A variation of `test_overwrite` that has a mapping which is only on one lint."""
        code = textwrap.dedent(
            """\
            project = "foo"

            release = version = "1.0.0"

            intersphinx_mapping = {"existing": "value", "another": "asdfasdf"}
            """
        )
        links = {"another": ("https://google.com", None), "existing": "value"}
        expected = textwrap.dedent(
            """\
            project = "foo"

            release = version = "1.0.0"

            intersphinx_mapping = {
                "another": ('https://google.com', None),
                "existing": "value",
            }
            """
        )
        self._test(expected, links, code)

    def test_overwrite_single_002(self):
        """A variation of `test_overwrite` that has a mapping which is only on one lint."""
        code = textwrap.dedent(
            """\
            project = "foo"

            release = version = "1.0.0"

            intersphinx_mapping = {"existing": "value", "another": "asdfasdf"
            }
            """
        )
        links = {"another": ("https://google.com", None), "existing": "value"}
        expected = textwrap.dedent(
            """\
            project = "foo"

            release = version = "1.0.0"

            intersphinx_mapping = {
                "another": ('https://google.com', None),
                "existing": "value",
            }
            """
        )
        self._test(expected, links, code)

    def test_syntax_error(self):
        """Check that a conf.py that contains a syntax error raises the correct exception."""
        code = textwrap.dedent(
            """\
            project = "foo"

            release = version =
            """
        )
        links = {"another": ("https://google.com", None), "existing": "value"}

        with tempfile.NamedTemporaryFile(
            suffix=".py", mode="w", delete=False
        ) as handler:
            handler.write(code)

        self.delete_item_later(handler.name)

        with self.assertRaises(exceptions.SphinxFileBroken):
            sphinx_helper.replace_intersphinx_mapping(links, handler.name)


class Replace(_Tester):
    """Change an existing ``intersphinx_mapping`` attribute either completely or partially."""

    def test_empty_001(self):
        """Replace a valid mapping with more keys."""
        code = textwrap.dedent(
            """\
            project = "foo"

            release = version = "1.0.0"

            intersphinx_mapping = dict()
            """
        )
        links = {"another": ("https://google.com", None), "tttt": ("some_url", None)}
        expected = textwrap.dedent(
            """\
            project = "foo"

            release = version = "1.0.0"

            intersphinx_mapping = {
                "another": ('https://google.com', None),
                "tttt": ('some_url', None),
            }
            """
        )
        self._test(expected, links, code)

    def test_empty_002(self):
        """Replace a valid mapping with more keys."""
        code = textwrap.dedent(
            """\
            project = "foo"

            release = version = "1.0.0"

            intersphinx_mapping = {}
            """
        )
        links = {"another": ("https://google.com", None), "tttt": ("some_url", None)}
        expected = textwrap.dedent(
            """\
            project = "foo"

            release = version = "1.0.0"

            intersphinx_mapping = {
                "another": ('https://google.com', None),
                "tttt": ('some_url', None),
            }
            """
        )
        self._test(expected, links, code)

    def test_single_001(self):
        """Add missing keys but retain the original keys."""
        code = textwrap.dedent(
            """\
            project = "foo"

            release = version = "1.0.0"

            intersphinx_mapping = { "existing": "value" }
            """
        )
        links = {"foo": ("https://google.com", None), "existing": "value"}
        expected = textwrap.dedent(
            """\
            project = "foo"

            release = version = "1.0.0"

            intersphinx_mapping = {
                "existing": "value",
                "foo": ('https://google.com', None),
            }
            """
        )
        self._test(expected, links, code)

    def test_single_002(self):
        """Add missing keys but retain the original keys."""
        code = textwrap.dedent(
            """\
            project = "foo"

            release = version = "1.0.0"

            intersphinx_mapping = {
                "existing": "value" }
            """
        )
        links = {"foo": ("https://google.com", None), "existing": "value"}
        expected = textwrap.dedent(
            """\
            project = "foo"

            release = version = "1.0.0"

            intersphinx_mapping = {
                "existing": "value",
                "foo": ('https://google.com', None),
            }
            """
        )
        self._test(expected, links, code)

    def test_single_003(self):
        """Add missing keys but retain the original keys."""
        code = textwrap.dedent(
            """\
            project = "foo"

            release = version = "1.0.0"

            intersphinx_mapping = {
                "existing": "value",
                }
            """
        )
        links = {"foo": ("https://google.com", None), "existing": "value"}
        expected = textwrap.dedent(
            """\
            project = "foo"

            release = version = "1.0.0"

            intersphinx_mapping = {
                "existing": "value",
                "foo": ('https://google.com', None),
            }
            """
        )
        self._test(expected, links, code)

    def test_single_004(self):
        """Add missing keys but retain the original keys."""
        code = textwrap.dedent(
            """\
            project = "foo"

            release = version = "1.0.0"

            intersphinx_mapping = {
                "existing": "value",
                }
            """
        )
        links = {"foo": ("https://google.com", None), "existing": "value"}
        expected = textwrap.dedent(
            """\
            project = "foo"

            release = version = "1.0.0"

            intersphinx_mapping = {
                "existing": "value",
                "foo": ('https://google.com', None),
            }
            """
        )
        self._test(expected, links, code)

    def test_multiple_001(self):
        """Add missing keys but retain the original keys."""
        code = textwrap.dedent(
            """\
            project = "foo"

            release = version = "1.0.0"

            intersphinx_mapping = { "existing": "value", "another": "asdfasdf" }
            """
        )
        links = {
            "another": "asdfasdf",
            "existing": "value",
            "foo": ("https://google.com", None),
        }
        expected = textwrap.dedent(
            """\
            project = "foo"

            release = version = "1.0.0"

            intersphinx_mapping = {
                "another": "asdfasdf",
                "existing": "value",
                "foo": ('https://google.com', None),
            }
            """
        )
        self._test(expected, links, code)

    def test_multiple_002(self):
        """Add missing keys but retain the original keys."""
        code = textwrap.dedent(
            """\
            project = "foo"

            release = version = "1.0.0"

            intersphinx_mapping = {
                "existing": "value",
                "another": "asdfasdf",
            }
            """
        )
        links = {
            "another": "asdfasdf",
            "existing": "value",
            "foo": ("https://google.com", None),
        }
        expected = textwrap.dedent(
            """\
            project = "foo"

            release = version = "1.0.0"

            intersphinx_mapping = {
                "another": "asdfasdf",
                "existing": "value",
                "foo": ('https://google.com', None),
            }
            """
        )
        self._test(expected, links, code)
