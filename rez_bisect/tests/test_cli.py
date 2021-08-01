#!/usr/bin/env python

import unittest

from rez_bisect import cli

from . import common, rez_common


class RunScenarios(unittest.TestCase):
    def test_bad_single_package(self):
        """Find the package which has some problem."""
        directory = common.make_directory()
        before, _ = rez_common.make_package(directory, version="1.0.0", is_bad=False)
        rez_common.make_package(directory, version="1.1.0", is_bad=False)
        first_bad = rez_common.make_package(directory, version="1.2.0", is_bad=True)
        rez_common.make_package(directory, version="1.2.1", is_bad=True)
        rez_common.make_package(directory, version="1.2.2", is_bad=True)
        after, checker = rez_common.make_package(directory, version="1.3.0", is_bad=True)

        cli.main(["run", after, checker, "--good", before])

    def test_command_any(self):
        """Run any shell command to find a specific problem."""
        raise ValueError("asdfs")

    def test_command_rez_test(self):
        """Run Rez tests to find a specific problem."""
        raise ValueError("asdfs")


class RunInputs(unittest.TestCase):
    """Make sure `run` works with a variety of input."""

    def test_context_file(self):
        """Read from a Rez resolve context file."""
        raise ValueError("asdfs")

    def test_context_json(self):
        """Read from a Rez resolve context json."""
        raise ValueError("asdfs")

    def test_request(self):
        """Resolve + Read from a Rez package request."""
        raise ValueError("asdfs")
