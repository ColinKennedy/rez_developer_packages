"""Make sure `rez-yum` works as expected."""

import atexit
import functools
import shutil
import tempfile
import shlex
import unittest

from python_compatibility import website
from rez_yum import cli


class Convert(unittest.TestCase):
    def test_convert_fail(self):
        raise ValueError()

    def test_no_file(self):
        raise ValueError()

    def test_permissions(self):
        raise ValueError()

    def test_simple_convert(self):
        raise ValueError()


@unittest.skipIf(website.is_internet_on(), "No Internet, skipping tests.")
class Download(unittest.TestCase):
    def test_not_found(self):
        raise ValueError()

    def test_found(self):
        raise ValueError()


class Install(unittest.TestCase):
    def test_dependencies_rpm(self):
        _test("rez-yum install gcc")

    def test_single_rpm(self):
        """Make sure --destination works and a single RPM is installed."""
        path = _make_directory("_Install_test_single_rpm")
        _test('install libXtst --destination "{path}"'.format(path=path))


class Miscellaneous(unittest.TestCase):
    def test_invalid_arguments(self):
        raise ValueError()


def _make_directory(name):
    directory = tempfile.mkdtemp(suffix=name)
    atexit.register(functools.partial(shutil.rmtree, directory))

    return directory


def _test(command):
    parts = shlex.split(command)

    namespace = cli.parse_arguments(parts)
    cli.run(namespace)
