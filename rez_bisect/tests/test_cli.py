#!/usr/bin/env python

"""Make sure :mod:`rez_bisect.cli` works as expected."""

import textwrap
import unittest

from rez_bisect import cli

from . import common, rez_common


class RunScenarios(unittest.TestCase):
    """Make sure `run` can properly bisect many different package scenarios."""

    def test_bad_single_package(self):
        """Find the package which has some problem."""
        directory = common.make_directory()

        versions = []

        for version in ["1.0.0", "1.1.0", "1.2.0", "1.2.1", "1.2.2", "1.3.0"]:
            versions.append(rez_common.make_context(directory, version=version))

        before = versions[0]
        after = versions[-1]

        # Note: In this `checker`, the first Rez package which has an
        # issue is 1.2.0. And all other packages after that point also
        # have the issue.
        #
        checker = common.make_script(
            textwrap.dedent(
                """\
                #!/usr/bin/env sh

                if [ "$REZ_FOO_VERSION" == "1.0.0" ] || [ "$REZ_FOO_VERSION" == "1.1.0" ]
                then
                    exit 0
                else
                    exit 1
                fi
                """
            )
        )

        cli.main(["run", before, after, checker])

    def test_exact_match(self):
        """Get the exact package where and issue occurs, in a large list of Rez packages."""
        directory = common.make_directory()

        for version in ["1.0.0", "1.1.0", "1.2.0", "1.2.1", "1.2.2", "1.3.0"]:
            versions.append(rez_common.make_context(directory, version=version))

        before = versions[0]
        after = versions[-1]

        # Note: In this `checker`, the first Rez package which has an
        # issue is 1.2.0. And all other packages after that point also
        # have the issue.
        #
        checker = common.make_script(
            textwrap.dedent(
                """\
                #!/usr/bin/env sh

                if [ "$REZ_FOO_VERSION" == "1.0.0" ] || [ "$REZ_FOO_VERSION" == "1.1.0" ]
                then
                    exit 0
                else
                    exit 1
                fi
                """
            )
        )

        cli.main(["run", before, after, checker])

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
