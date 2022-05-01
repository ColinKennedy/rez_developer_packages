import os
import unittest

from .common import utility

_CURRENT_DIRECTORY = os.path.dirname(os.path.realpath(__file__))
_TESTS = os.path.join(os.path.dirname(_CURRENT_DIRECTORY), "_test_data")


class Cases(unittest.TestCase):
    def test_newer_package_001(self):
        """Find the first package to include a dependency which causes failure."""

        def _is_failure_condition(context):
            return context.get_resolved_package("dependency") is not None

        directory = os.path.join(_TESTS, "simple_packages")

        bad_version = "1.2.0"
        request_1 = "changing_dependencies==1.0.0"
        request_2 = "changing_dependencies==1.1.0"
        request_3 = "changing_dependencies=={bad_version}".format(
            bad_version=bad_version
        )
        request_4 = "changing_dependencies==1.3.0"

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

    def test_downversion(self):
        """Fail when a package version goes below a certain point."""
        raise ValueError()

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
