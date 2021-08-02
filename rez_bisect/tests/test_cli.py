#!/usr/bin/env python

"""Make sure :mod:`rez_bisect.cli` works as expected."""

import itertools
import textwrap
import math
import unittest

from python_compatibility import wrapping
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
                fi

                exit 1
                """
            )
        )

        with wrapping.capture_pipes() as (stdout, stderr):
            cli.main(["run", before, after, checker])

        self.assertFalse(stderr.getvalue())
        self.assertEqual(
            textwrap.dedent(
                """\
                These added / removed / changed packages are the cause of the issue:
                    newer_packages
                        foo-1.2.0
                """
            ),
            stdout.getvalue(),
        )

    def test_command_never_succeeds(self):
        """Fail gracefully if the user-provided command does not actually succeed."""
        raise
        # def _get_versions(major, weight, count):
        #     return [
        #         "{major}.{value}.0".format(major=major, value=value)
        #         for value in range(math.floor(count * weight))
        #     ]
        #
        # weight = 0.63
        # count = 5
        #
        # good_versions = _get_versions(1, weight, count)
        # bad_versions = _get_versions(2, 1 - weight, count)
        #
        # directory = common.make_directory()
        # versions = []
        #
        # for version in itertools.chain(good_versions, bad_versions):
        #     versions.append(rez_common.make_context(directory, version=version))
        #
        # before = versions[0]
        # after = versions[-1]
        #
        # # Note: In this `checker`, the first Rez package which has an
        # # issue is 1.2.0. And all other packages after that point also
        # # have the issue.
        # #
        # checker = common.make_script(
        #     textwrap.dedent(
        #         """\
        #         #!/usr/bin/env sh
        #
        #         if [[ "$REZ_FOO_VERSION" == 1* ]]
        #         then
        #             exit 0
        #         fi
        #
        #         exit 1
        #         """
        #     )
        # )
        #
        # cli.main(["run", before, after, checker])

    def test_dropped_dependency(self):
        """Find the Rez dependency which was dropped between versions.

        If 2 Rez packages depend on something but only one of them lists
        it in their `requires` attribute, if the dependency is dropped,
        the other Rez package may fail.

        This scenario covers that situation.

        """
        raise ValueError("asdf")

    def test_exact_match(self):
        """Get the exact package where and issue occurs, in a large list of Rez packages."""

        def _get_versions(major, weight, count):
            return [
                "{major}.{value}.0".format(major=major, value=value)
                for value in range(math.floor(count * weight))
            ]

        weight = 0.63
        count = 300

        good_versions = _get_versions(1, weight, count)
        bad_versions = _get_versions(2, 1 - weight, count)

        directory = common.make_directory()
        versions = []

        for version in itertools.chain(good_versions, bad_versions):
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

                if [[ "$REZ_FOO_VERSION" == 1* ]]
                then
                    exit 0
                fi

                exit 1
                """
            )
        )

        with wrapping.capture_pipes() as (stdout, stderr):
            cli.main(["run", before, after, checker])

        self.assertFalse(stderr.getvalue())
        self.assertEqual(
            textwrap.dedent(
                """\
                These added / removed / changed packages are the cause of the issue:
                    newer_packages
                        foo-2.0.0
                """
            ),
            stdout.getvalue(),
        )

    def test_multiple_bad_configurations(self):
        """A resolve where 4 packages all have the same fail condition."""
        raise ValueError()


class RunInputs(unittest.TestCase):
    """Make sure `run` works with a variety of input."""

    def test_command_any(self):
        """Run any shell command to find a specific problem."""
        raise ValueError("asdfs")

    def test_command_rez_test(self):
        """Run Rez tests to find a specific problem."""
        raise ValueError("asdfs")

    def test_context_file(self):
        """Read from a Rez resolve context file."""
        raise ValueError("asdfs")

    def test_context_json(self):
        """Read from a Rez resolve context json."""
        raise ValueError("asdfs")

    def test_request(self):
        """Resolve + Read from a Rez package request."""
        raise ValueError("asdfs")
