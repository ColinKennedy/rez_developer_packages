from __future__ import print_function

import atexit
import contextlib
import functools
import io
import os
import shlex
import shutil
import sys
import tempfile
import textwrap
import unittest

from rez_docbot import cli
from rez_docbot.commands.builder_registries import builder_registry


class DelimiterCases(unittest.TestCase):
    def test_build_plugin_help(self):
        """Show the help directly from the builder plug-in."""
        with self.assertRaises(SystemExit), _capture_stream() as stdout:
            _run("rez_docbot build sphinx -- --help")

        text = stdout.getvalue()
        expected = textwrap.dedent(
            """\
            usage: python -m unittest [-h] [--source SOURCE] [--destination DESTINATION]

            Tell Sphinx where the documentation lives and where to build it.

            optional arguments:
              -h, --help            show this help message and exit
              --source SOURCE       The root folder containing your index.rst (or
                                    equivalent file).
              --destination DESTINATION
                                    The folder to build all documentation into.
            """
        )

        self.assertEqual(expected, text)

    def test_build_rez_help_001(self):
        """Show the help for builder plug-ins."""
        with self.assertRaises(SystemExit), _capture_stream() as stdout:
            _run("rez_docbot build --help")

        text = stdout.getvalue()

        expected = textwrap.dedent(
            """\
            usage: python -m unittest build [-h] {sphinx}

            positional arguments:
              {sphinx}    The plugin to build with. e.g. `sphinx`.

            optional arguments:
              -h, --help  show this help message and exit
            """
        )

        self.assertEqual(expected, text)

    def test_build_rez_help_002(self):
        with self.assertRaises(SystemExit), _capture_stream() as stdout:
            _run("rez_docbot build sphinx --help")

        text = stdout.getvalue()
        expected = textwrap.dedent(
            """\
            usage: python -m unittest [-h] [--source SOURCE] [--destination DESTINATION]

            Tell Sphinx where the documentation lives and where to build it.

            optional arguments:
              -h, --help            show this help message and exit
              --source SOURCE       The root folder containing your index.rst (or
                                    equivalent file).
              --destination DESTINATION
                                    The folder to build all documentation into.
            """
        )
        self.assertEqual(expected, text)

    def test_general_help(self):
        """Show the general help."""
        with self.assertRaises(SystemExit), _capture_stream() as stdout:
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

    def test_incomplete_left_arguments(self):
        with self.assertRaises(SystemExit), _capture_stream(stream="stderr") as stream:
            _run("rez_docbot -- --help")

        text = stream.getvalue()

        expected = textwrap.dedent(
            """\
            usage: python -m unittest [-h] {build,publish} ...
            python -m unittest: error: invalid choice: '--' (choose from 'build', 'publish')
            """
        )

        self.assertEqual(expected, text)


class BuilderRegistry(unittest.TestCase):
    """Ensure builder plug-ins can be found and executed as expected."""

    def setUp(self):
        self._environment = os.environ.copy()
        self._path = list(sys.path)

    def tearDown(self):
        builder_registry.clear_user_plugins()

        os.environ.clear()
        os.environ.update(self._environment)
        sys.path[:] = []
        sys.path.extend(self._path)

    def test_not_found(self):
        """Error if the provided plug-in name does not exist."""
        with self.assertRaises(SystemExit), _capture_stream(stream="stderr") as stream:
            _run("rez_docbot build does_not_exist")

        text = stream.getvalue()
        expected = textwrap.dedent(
            """\
            usage: python -m unittest build [-h] {sphinx}
            python -m unittest build: error: argument builder: invalid choice: 'does_not_exist' (choose from 'sphinx')
            """
        )

        self.assertEqual(expected, text)

    def test_found_known(self):
        """Find a provided plug-in."""
        with self.assertRaises(SystemExit), _capture_stream(stream="stderr"):
            _run("rez_docbot build sphinx")

    def test_found_user(self):
        """Find a user-provided plug-in."""

        def _make_user_module():
            directory = tempfile.mkdtemp(suffix="_test_found_user")
            atexit.register(functools.partial(shutil.rmtree, directory))

            module = os.path.join(directory, "some_package", "thing.py")
            os.makedirs(os.path.dirname(module))

            with open(module, "w") as handler:
                handler.write(
                    textwrap.dedent(
                        """\
                        import rez_docbot

                        class MyPlugin(rez_docbot):
                            @staticmethod
                            def get_name():
                                return "user-plugin"

                            def parse_arguments(text):
                                parser = argparse.ArgumentParser(description="Add any arguments you'd like, here")
                                parser.add_argument("--your", help="Some argument.")
                                parser.add_argument("--arguments", help="Some argument.", choices=("bar", "another"))
                                parser.add_argument("--here", help="Some argument.", actions="store_true")

                                return parser.parse_args(text)

                            def build(namespace):
                                pass
                        """
                    )
                )

            return directory, "some_package.thing"

        def _simulate_initialization():
            directory, namespace = _make_user_module()

            sys.path.append(directory)
            os.environ[builder_registry._USER_PLUGIN_ENVIRONMENT_VARIABLE] = namespace

            builder_registry.register_user_plugins()

        _simulate_initialization()

        with self.assertRaises(SystemExit), _capture_stream(stream="stderr") as stream:
            _run("rez_docbot build user-plugin")

        text = stream.getvalue()
        raise ValueError(text)
        expected = textwrap.dedent("asdf")

        self.assertEqual(expected, text)


@contextlib.contextmanager
def _capture_stream(stream="stdout"):
    # TODO : Replace this with a proper mock.patch, later
    output = io.BytesIO()

    if stream == "stdout":
        original = sys.stdout
        sys.stdout = output
    elif stream == "stderr":
        original = sys.stderr
        sys.stderr = output
    else:
        raise NotImplementedError(stream)

    try:
        yield output
    finally:
        if stream == "stdout":
            sys.stdout = original
        elif stream == "stderr":
            sys.stderr = original
        else:
            raise NotImplementedError(stream)


def _run(text):
    items = shlex.split(text)

    if items[0] == "rez_docbot":
        del items[0]

    cli.main(items)
