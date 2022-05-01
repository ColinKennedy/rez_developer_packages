"""Make sure :ref:`--partial` behavior works as expected."""

import os
import unittest

from rez.vendor.version import version
from .common import utility

_CURRENT_DIRECTORY = os.path.dirname(os.path.realpath(__file__))
_TESTS = os.path.join(os.path.dirname(_CURRENT_DIRECTORY), "_test_data")

_FOO_LOW_VERSION = version.Version("1.5.0")


# TODO : I think all of these tests need to be modified to be more fluid. Most
# of the tests version ranges are exact version matches when they should be
# version ranges. Or they need to mix / match different unrelated packages in
# the overall request to hide the actual issue.
#
class Cases(unittest.TestCase):
    """Known bisect :ref:`--partial` scenarios to always get right."""

    def test_newer_package_001(self):
        """Find the first package to include a dependency which causes failure."""

        def _is_failure_condition(context):
            return context.get_resolved_package("dependency") is not None

        directory = os.path.join(_TESTS, "simple_packages")

        bad_version = "1.2.0"
        request_1 = "changing_dependencies-1+<1.2"
        request_2 = "changing_dependencies==1.2.0"

        with utility.patch_run(_is_failure_condition):
            result = utility.run_test(
                [
                    "run",
                    "",
                    request_1,
                    request_2,
                    "--packages-path",
                    directory,
                    "--partial",
                ]
            )

        self.assertEqual(0, result.last_good)
        self.assertEqual(1, result.first_bad)
        self.assertEqual({"newer_packages"}, set(result.breakdown.keys()))
        self.assertEqual(
            {("changing_dependencies", bad_version)},
            {
                (package.name, str(package.version))
                for package in result.breakdown["newer_packages"]
            },
        )

    def test_newer_package_002(self):
        """Find the first package to exclude a dependency, resulting in failure."""

        def _is_failure_condition(context):
            return context.get_resolved_package("bar") is None

        directory = os.path.join(_TESTS, "simple_packages")

        bad_version = "1.6.0"
        request_1 = "changing_dependencies==1.4.0"
        request_2 = "changing_dependencies==1.5.0"
        request_3 = "changing_dependencies=={bad_version}".format(
            bad_version=bad_version
        )
        request_4 = "changing_dependencies==1.7.0"

        with utility.patch_run(_is_failure_condition):
            result = utility.run_test(
                [
                    "run",
                    "",
                    request_1,
                    request_2,
                    request_3,
                    request_4,
                    "--packages-path",
                    directory,
                    "--partial",
                ]
            )

        self.assertEqual(1, result.last_good)
        self.assertEqual(2, result.first_bad)
        self.assertEqual({"newer_packages"}, set(result.breakdown.keys()))
        self.assertEqual(
            {("changing_dependencies", bad_version)},
            {
                (package.name, str(package.version))
                for package in result.breakdown["newer_packages"]
            },
        )

    def test_down_version(self):
        """Fail when a package version goes below a certain point."""

        def _is_failure_condition(context):
            return context.get_resolved_package("foo").version < _FOO_LOW_VERSION

        directory = os.path.join(_TESTS, "simple_packages")

        command = [
            "run",
            "",
            "foo-1.6 dependency",
            "foo-1+<1.4 bar-1",
            "--packages-path",
            directory,
            "--partial",
        ]

        with utility.patch_run(_is_failure_condition):
            result = utility.run_test(command)

        self.assertEqual(0, result.last_good)
        self.assertEqual(1, result.first_bad)

        bad_version = "1.4.0"  # This version is "bad" because it's less than "1.5.0"

        self.assertEqual({"older_packages"}, set(result.breakdown.keys()))
        self.assertEqual(
            {("foo", bad_version)},
            {
                (package.name, str(package.version))
                for package in result.breakdown["older_packages"]
            },
        )

    def test_removed(self):
        """Fail when some important package was removed from the request."""

        def _is_failure_condition(context):
            return context.get_resolved_package("foo") is None

        directory = os.path.join(_TESTS, "simple_packages")

        request_1 = "changing_dependencies-1.4 foo-1.1+<2"
        request_2 = "changing_dependencies==1.5.0 foo-1.1+<2"
        request_3 = "changing_dependencies-1.5+<2"
        request_4 = "changing_dependencies-1.5+<2"

        with utility.patch_run(_is_failure_condition):
            result = utility.run_test(
                [
                    "run",
                    "",
                    request_1,
                    request_2,
                    request_3,
                    request_4,
                    "--packages-path",
                    directory,
                    "--partial",
                ]
            )

        raise ValueError(result)
        self.assertEqual(1, result.last_good)
        self.assertEqual(2, result.first_bad)
        self.assertEqual({"newer_packages"}, set(result.breakdown.keys()))
        self.assertEqual(
            {("changing_dependencies", bad_version)},
            {
                (package.name, str(package.version))
                for package in result.breakdown["newer_packages"]
            },
        )
