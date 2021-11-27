from __future__ import print_function

import contextlib
import io
import shlex
import sys
import textwrap
import unittest

from rez_docbot import cli


class DelimiterCases(unittest.TestCase):
    def test_build_rez_help(self):
        """Show the help for builder plug-ins."""
        with self.assertRaises(SystemExit), _capture_prints() as stdout:
            _run("rez_docbot build --help")

        text_1 = stdout.getvalue()

        with self.assertRaises(SystemExit), _capture_prints() as stdout:
            _run("rez_docbot build sphinx --help")

        text_2 = stdout.getvalue()

        expected = textwrap.dedent(
            """\
            usage: python -m unittest build [-h] {sphinx}

            positional arguments:
              {sphinx}    The plugin to build with. e.g. `sphinx`.

            optional arguments:
              -h, --help  show this help message and exit
            """
        )

        self.assertEqual(expected, text_1)
        self.assertEqual(expected, text_2)

    def test_general_help(self):
        """Show the general help."""
        with self.assertRaises(SystemExit), _capture_prints() as stdout:
            _run("rez_docbot --help")

        text = stdout.getvalue()
        expected = textwrap.dedent(
            """\
            usage: python -m unittest [-h] {build,publish} ...

            The main CLI which contains sub-commands.

            positional arguments:
              {build,publish}
                publish        Send data to some external location. e.g. Send to GitHub.

            optional arguments:
              -h, --help       show this help message and exit
            """
        )

        self.assertEqual(expected, text)

    def test_help_with_no_delimiter(self):
        raise ValueError()

    def test_incomplete_left_arguments(self):
        raise ValueError()

    def test_incomplete_right_arguments(self):
        raise ValueError()

    def test_help_is_left_of_delimiter(self):
        """Show the general help."""
        raise ValueError()

    def test_help_is_right_of_delimiter(self):
        """Show the plug-in help."""
        raise ValueError()


class BuilderRegistry(unittest.TestCase):
    """Ensure builder plug-ins can be found and executed as expected."""

    def test_not_found(self):
        """Error if the provided plug-in name does not exist."""
        raise ValueError()

    def test_found_known(self):
        """Find a provided plug-in."""
        raise ValueError()

    def test_found_user(self):
        """Find a user-provided plug-in."""
        raise ValueError()


def _run(text):
    items = shlex.split(text)

    if items[0] == "rez_docbot":
        del items[0]

    cli.main(items)


@contextlib.contextmanager
def _capture_prints():
    stdout = io.BytesIO()

    original = sys.stdout
    sys.stdout = stdout

    try:
        yield stdout
    finally:
        sys.stdout = original

    atexit.register(stdout.close)
