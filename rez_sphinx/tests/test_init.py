"""Make sure :ref:`rez_sphinx init` works as expected."""

import atexit
import functools
import os
import shlex
import shutil
import tempfile
import textwrap
import unittest

from rez_sphinx import cli


class Init(unittest.TestCase):
    """Make sure :ref:`rez_sphinx init` works with expected cases."""

    def test_hello_world(self):
        """Initialize a very simple Rez package with Sphinx documentation."""
        directory = _make_simple_developer_package()
        _test('init "{directory}"'.format(directory=directory))


class Invalids(unittest.TestCase):
    """Make sure :ref:`rez_sphinx init` fails when it's supposed to fail."""

    # TODO : Do these
    # def test_bad_permissions(self):
    #     raise ValueError()
    # def test_no_package(self):
    #     """Fail early if the user isn't in a Rez package."""
    #     raise ValueError()
    #
    # def test_no_python_files(self):
    #     """Fail early if there aren't Python files."""
    #     raise ValueError()


def _delete_later(directory):
    atexit.register(functools.partial(shutil.rmtree, directory))


def _make_simple_developer_package():
    directory = tempfile.mkdtemp(suffix="_make_simple_developer_package")
    _delete_later(directory)

    with open(os.path.join(directory, "package.py"), "w") as handler:
        handler.write(
            textwrap.dedent(
                """\
                name = "some_package"

                def commands():
                    import os

                    os.path.join(root, "python")
                """
            )
        )

    python_directory = os.path.join(directory, "python")
    os.makedirs(python_directory)

    with open(os.path.join(python_directory, "file.py"), "w") as handler:
        handler.write('print("Hello, World!")')

    return directory


def _test(text):
    parts = shlex.split(text)
    cli.main(parts)
