import shlex
import unittest

from rez_sphinx import cli


class Cli(unittest.TestCase):
    def test_build(self):
        raise ValueError()

    def test_check(self):
        raise ValueError()

class Create(unittest.TestCase):
    def test_custom_arguments(self):
        """Make sure a basic `create` command works."""
        raise ValueError()
        # _test("create")

    def test_default(self):
        """Make sure a basic `create` command works."""
        _test("create")

    def test_out_of_rez(self):
        """Prevent the user from building documentation outside a Rez package."""
        raise ValueError()


class Invalid(unittest.TestCase):
    def test_not_in_rez_folder(self):
        raise ValueError()

    def test_no_source_folder(self):
        raise ValueError()


class Options(unittest.TestCase):
    def test_automatic_rst_files(self):
        raise ValueError()


def _test(command):
    cli.main(shlex.split(command))
