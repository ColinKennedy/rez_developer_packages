"""Make sure the :ref:`rez_bisect run` works as expected."""

import contextlib
import os
import shlex
import unittest

import six
from six.moves import mock

from rez_bisect import cli


_CURRENT_DIRECTORY = os.path.dirname(os.path.realpath(__file__))
_TESTS = os.path.join(os.path.dirname(_CURRENT_DIRECTORY), "_test_data")


class BadRequestCheck(unittest.TestCase):
    """Ensure start / end contexts and others work as expected."""

    def test_end_001(self):
        """Fail if the end request fails to resolve."""
        raise ValueError()

    def test_end_002(self):
        """Fail if the end request does not have the script issue."""
        raise ValueError()

    def test_start_001(self):
        """Fail if the start request fails to resolve."""
        raise ValueError()

    def test_start_002(self):
        """Fail if the start request has the script issue."""
        raise ValueError()


class Invalids(unittest.TestCase):
    def test_script_not_found(self):
        raise ValueError()


class Cases(unittest.TestCase):
    """Ensure bisecting detects expected issues."""

    def test_included_family_bad(self):
        raise ValueError()


class CasePositioning(unittest.TestCase):

    def test_three(self):
        """Including a Rez package family creates some kind of issue."""

        def _is_failure_condition(context):
            return context.get_resolved_package("bar") is not None

        directory = os.path.join(_TESTS, "simple_packages")

        request_1 = "foo==1.0.0"
        request_2 = "foo==1.1.0"
        request_3 = "foo==1.2.0 bar==1.0.0"

        with _patch_run(_is_failure_condition):
            result = _run_test(["run", "", request_1, request_2, request_3, "--packages-path", directory])

        self.assertEqual(1, result.first_bad)

    def test_permutations(self):
        """Including a Rez package family creates some kind of issue."""

        def _quick_test(expected, maximum=20):
            for count in range(2, maximum):
                if count < expected:
                    continue

                result = _build_bad_index_case(expected, count)
                self.assertEqual(
                    expected,
                    result,
                    msg='Count "{count}" expected "{expected}" but got "{result}" '
                    'result.'.format(count=count, expected=expected, result=result),
                )

        _quick_test(1)
        _quick_test(4)
        _quick_test(10)
        _quick_test(14)
        _quick_test(17)
        _quick_test(19)


@contextlib.contextmanager
def _patch_run(checker):
    with mock.patch(
        "rez_bisect.cli._validate_script"
    ), mock.patch(
        "rez_bisect.core.rez_helper.to_script_runner", wraps=checker,
    ) as patch:
        patch.return_value = checker

        yield


def _build_bad_index_case(bad_index, count):

    def _is_failure_condition(context):
        return context.get_resolved_package("bar") is not None

    directory = os.path.join(_TESTS, "simple_packages")

    requests = [
        "foo==1.{index}.0 bar==1.0.0".format(index=index)
        if index >= bad_index
        else "foo==1.{index}.0".format(index=index)
        for index in range(count)
    ]

    command = ["run", ""]
    command.extend(requests)
    command.extend(["--packages-path", directory])

    with _patch_run(_is_failure_condition):
        result = _run_test(command)

    return result.first_bad


def _run_test(command):
    if isinstance(command, six.string_types):
        command = shlex.split(command)

    namespace = cli.parse_arguments(command)

    return cli.run(namespace)
