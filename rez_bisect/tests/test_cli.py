#!/usr/bin/env python

"""Make sure :mod:`rez_bisect.cli` works as expected."""

import itertools
import os
import functools
import textwrap
import math
import unittest

from python_compatibility import wrapping
from rez_bisect.core import exception
from rez_bisect import cli

from . import common, rez_common


class Diff(unittest.TestCase):
    """Make sure every key in Rez's diff is supported."""

    def test_added(self):
        """Make sure an issue caused by multiple added packages is detectable."""
        raise ValueError()

    def test_older(self):
        """Make sure an issue caused by multiple older packages is detectable."""
        raise ValueError()

    def test_removed(self):
        """Make sure an issue caused by multiple removed packages is detectable."""
        raise ValueError()


class Ephemerals(unittest.TestCase):
    def test_single_added(self):
        """Check that adding a single ephemeral causes a fail."""
        raise ValueError()

    def test_single_removed(self):
        """Check that removing a single ephemeral causes a fail."""
        raise ValueError()

    def test_multiple_added(self):
        """Check that adding a multiple ephemeral causes a fail."""
        raise ValueError()

    def test_multiple_removed(self):
        """Check that removing a multiple ephemeral causes a fail."""
        raise ValueError()


class Scenarios(unittest.TestCase):
    """Make sure `run` can properly bisect many different package scenarios."""

    def test_bad_single_package(self):
        """Find the package which has some problem."""
        directory = common.make_directory()

        versions = []

        for version in ["1.0.0", "1.1.0", "1.2.0", "1.2.1", "1.2.2", "1.3.0"]:
            versions.append(rez_common.make_single_context(directory, version=version))

        before = versions[0]
        after = versions[-1]

        # Note: In this `checker`, the first Rez package which has an
        # issue is 1.2.0. And all other packages after that point also
        # have the issue.
        #
        checker = common.make_temporary_script(
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
        raise ValueError()
        # TODO : Make sure this is a CLI call which ignores the good/bad check
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
        #     versions.append(rez_common.make_single_context(directory, version=version))
        #
        # before = versions[0]
        # after = versions[-1]
        #
        # # Note: In this `checker`, the first Rez package which has an
        # # issue is 1.2.0. And all other packages after that point also
        # # have the issue.
        # #
        # checker = common.make_temporary_script(
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

    def test_dependency_added_001(self):
        """Catch when a dependency is added that causes some kind of issue."""
        raise ValueError()

    def test_dependency_added_002(self):
        """Catch when a dependency is added that causes some kind of issue.

        This method differs from :meth:`test_dependency_added_001`
        because "after" Rez context has packages which are older than
        they were previously. (In a real world scenario, this happens
        when someone does a rollback, due to some issue with the latest
        version releases, usually).

        """
        raise ValueError()

    def test_dependency_dropped_multiple(self):
        """Find the Rez dependencies which was dropped between versions.

        This variant of :meth:`RunScenarios.test_dependency_dropped`
        checks for multiple deleted dependencies at once.

        """
        raise ValueError()

    def test_dependency_dropped(self):
        """Find the Rez dependency which was dropped between versions.

        If 3 Rez packages depend on a package but only 2 of them lists
        it in their `requires` attribute, once those packages drop the
        dependency, the 3rd package will fail because it still uses the
        dependency but now fails.

        This scenario covers that situation.

        """
        directory = common.make_directory()
        rez_common.make_variant(directory, name="dependency", version="1.0.0")
        _make_variant = functools.partial(rez_common.make_variant, directory)

        # Make 2 packages which each drop `dependency` at some point
        before_a = _make_variant(name="a", version="1.0.0", requires=["dependency-1"])
        _make_variant(name="a", version="1.1.0", requires=["dependency-1"])
        _make_variant(name="a", version="1.1.1")
        _make_variant(name="a", version="1.2.0")
        _make_variant(name="a", version="1.3.0")
        after_a = _make_variant(name="a", version="1.3.1")
        before_b = _make_variant(name="b", version="3.0.0", requires=["dependency-1"])
        _make_variant(name="b", version="3.1.0", requires=["dependency-1"])
        _make_variant(name="b", version="3.1.1", requires=["dependency-1"])
        _make_variant(name="b", version="3.2.0", requires=["dependency-1"])
        _make_variant(name="b", version="3.3.0", requires=["dependency-1"])
        after_b = _make_variant(name="b", version="3.3.1")

        # Add a 3rd package that always depends on `dependency` but
        # doesn't explicitly state it, in its list of requirements.
        #
        variant = rez_common.make_variant(
            directory,
            name="c",
            version="1.0.0",
            commands=textwrap.dedent(
                """\
                def commands():
                    import os

                    env.PATH.append(os.path.join(root, "bin"))
                """
            ),
        )

        root = os.path.join(
            variant.resource.location, variant.name, str(variant.version)
        )
        checker = os.path.join(root, "bin", "something.sh")

        common.make_script(
            checker,
            textwrap.dedent(
                """\
                #!/usr/bin/env sh

                if [ ! -z "$REZ_DEPENDENCY_ROOT" ]
                then
                    exit 0
                fi

                exit 1
                """
            ),
        )

        before = rez_common.make_combined_context([before_a, before_b])
        after = rez_common.make_combined_context([after_a, after_b])

        with wrapping.capture_pipes() as (stdout, stderr):
            cli.main(["run", before, after, checker])

        self.assertFalse(stderr.getvalue())
        self.assertEqual(
            textwrap.dedent(
                """\
                These added / removed / changed packages are the cause of the issue:
                    newer_packages
                        a-1.1.1
                        b-3.3.1
                """
            ),
            stdout.getvalue(),
        )

    def test_dependency_rollback(self):
        """Check if a dependency dropped due to a package version rolling back is caught."""
        raise ValueError()

    def test_earliest_fails_001(self):
        """Detect if the earliest package is the failing package.

        As in

        (bad resolve)
        a-1.0.0 - good
        a-1.1.0 - bad  <-- We need to detect this bad point
        a-1.2.0 - bad
        a-1.3.0 - bad

        Note: We check for the second, not the first, because if the first failed
        then it means that there isn't a single version of package "a" were the resolve is "good".
        And of course, that would be a user error.

        """
        raise ValueError()

    def test_earliest_fails_002(self):
        """Detect if the earliest package is the failing package.

        As in

        (bad resolve)
        a-1.0.0 - bad  <-- We need to detect this bad point
        a-1.1.0 - bad
        a-1.2.0 - bad
        a-1.3.0 - bad

        This is user error. It means that they didn't provide a "good"
        resolve to compare against.

        """
        raise ValueError()

    def test_environment(self):
        """Run a bisect on a large, production-ish environment.

        We need at least one test like this. Most of the tests are too
        simply to be considered a real production case.

        """
        raise ValueError()

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
            versions.append(rez_common.make_single_context(directory, version=version))

        before = versions[0]
        after = versions[-1]

        # Note: In this `checker`, the first Rez package which has an
        # issue is 1.2.0. And all other packages after that point also
        # have the issue.
        #
        checker = common.make_temporary_script(
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

    def test_latest_fails(self):
        """Detect if the latest package is the only failing package.

        As in

        (bad resolve)
        a-1.0.0 - good
        a-1.1.0 - good
        a-1.2.0 - good
        a-1.3.0 - bad  <-- We need to detect this bad point

        """
        raise ValueError()

    def test_many_rez_packages(self):
        """Find the bad resolve which requires many Rez packages to replicate.

        This test is a variant of
        :meth:`RunScenarios.test_multiple_rez_packages`. The difference
        is, this method uses many more Rez packages to replicate the
        fault.

        """
        raise ValueError()

    def test_multiple_bad_configurations(self):
        """A resolve where 4 packages all have the same fail condition."""
        raise ValueError()

    def test_multiple_rez_packages(self):
        """Find the bad resolve which requires at least 2 Rez packages to replicate.

        This scenario is when both packages are "okay" in isolation but
        not together at the same time. This can be pretty common with
        lower-level C++ libraries, where 2 packages are incompatible but
        may still resolve (for whatever reason).

        """
        raise ValueError()

    def test_resolve_fail(self):
        """Simulate and fix when a middle resolve fails, mid-bisect.

        The bisect code will need to find a way to detect the bad
        resolve and adjust itself so it can keep testing, but with a
        different-but-similar resolve.

        """
        raise ValueError()


class Invalids(unittest.TestCase):
    """Make sure invalid input is detected and fails gracefully."""

    def test_not_bad(self):
        """Fail evaluation because the user's "bad" context passes their "command"."""
        directory = common.make_directory()

        versions = []

        for version in ["1.0.0", "1.1.0", "1.3.0"]:
            versions.append(rez_common.make_single_context(directory, version=version))

        before = versions[0]
        after = versions[-1]

        checker = common.make_temporary_script(
            textwrap.dedent(
                """\
                #!/usr/bin/env sh

                exit 0
                """
            )
        )

        with wrapping.capture_pipes() as (stdout, stderr):
            with self.assertRaises(exception.IsNotBad):
                cli.main(["run", before, after, checker])

    def test_not_good(self):
        """Fail evaluation because the user's "good" context doesn't pass their "command"."""
        directory = common.make_directory()

        versions = []

        for version in ["1.0.0", "1.1.0", "1.3.0"]:
            versions.append(rez_common.make_single_context(directory, version=version))

        before = versions[0]
        after = versions[-1]

        checker = common.make_temporary_script(
            textwrap.dedent(
                """\
                #!/usr/bin/env sh

                exit 1
                """
            )
        )

        with wrapping.capture_pipes() as (stdout, stderr):
            with self.assertRaises(exception.IsNotGood):
                cli.main(["run", before, after, checker])


class Inputs(unittest.TestCase):
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
