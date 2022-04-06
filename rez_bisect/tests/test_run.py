"""Make sure the :ref:`rez_bisect run` works as expected."""

import atexit
import contextlib
import functools
import os
import shlex
import tempfile
import unittest

import six
from rez.vendor.version import version
from rez import resolved_context
from six.moves import mock

from rez_bisect import cli
from rez_bisect.core import exception, rez_helper

_CURRENT_DIRECTORY = os.path.dirname(os.path.realpath(__file__))
_TESTS = os.path.join(os.path.dirname(_CURRENT_DIRECTORY), "_test_data")

_VERSION_1_1 = version.Version("1.1")
_VERSION_1_2 = version.Version("1.2")


class Cases(unittest.TestCase):
    """Ensure bisecting detects expected issues.

    Most of the unittests listed here are actually redundant and already
    covered elsewhere. That said, we cannot allow these cases to ever
    accidentally not work so these tests are here to "be explicit" about what
    should always work.

    """

    def test_bad_variant(self):
        """Fail once a specific variant is selected in a resolve."""
        raise ValueError()

    def test_bad_versions(self):
        """Fail once a certain version range occurs."""

        def _is_failure_condition(context):
            return context.get_resolved_package("foo").version > _VERSION_1_2

        directory = os.path.join(_TESTS, "simple_packages")

        request_1 = "foo==1.0.0"
        request_2 = "foo==1.1.0 bar-1"
        request_3 = "foo==1.2.0 bar-1"

        with _patch_run(_is_failure_condition):
            result = _run_test(
                [
                    "run",
                    "",
                    request_1,
                    request_2,
                    request_3,
                    "--packages-path",
                    directory,
                ]
            )

        self.assertEqual(2, result.first_bad)

    def test_included_family(self):
        """Fail when a bad Rez :ref:`package family` is added."""

        def _is_failure_condition(context):
            return context.get_resolved_package("bar") is not None

        directory = os.path.join(_TESTS, "simple_packages")

        request_1 = "foo==1.0.0"
        request_2 = "foo==1.1.0 bar-1"
        request_3 = "foo==1.2.0 bar-1"

        with _patch_run(_is_failure_condition):
            result = _run_test(
                [
                    "run",
                    "",
                    request_1,
                    request_2,
                    request_3,
                    "--packages-path",
                    directory,
                ]
            )

        self.assertEqual(1, result.first_bad)

    def test_removed_family(self):
        """Fail when a needed Rez :ref:`package family` is removed."""

        def _is_failure_condition(context):
            return context.get_resolved_package("bar") is None

        directory = os.path.join(_TESTS, "simple_packages")

        request_1 = "foo==1.0.0 bar-1"
        request_2 = "foo==1.1.0"
        request_3 = "foo==1.2.0"

        with _patch_run(_is_failure_condition):
            result = _run_test(
                [
                    "run",
                    "",
                    request_1,
                    request_2,
                    request_3,
                    "--packages-path",
                    directory,
                ]
            )

        self.assertEqual(1, result.first_bad)


class ContextInputs(unittest.TestCase):
    """Make sure bisect :ref:`request` and :ref:`.rxt` files behave as expected."""

    def test_failed_intermediary_context(self):
        """Make sure failed contexts are not allowed to continue."""

        def _is_failure_condition(context):
            return str(context.get_resolved_package("foo").version) == "1.0.0"

        directory = os.path.join(_TESTS, "simple_packages")

        with _patch_run(_is_failure_condition), self.assertRaises(exception.BadRequest):
            _run_test(
                [
                    "run",
                    "",
                    "foo==1.0.0",
                    "foo==1.1.0 !foo-1",
                    "foo==1.2.0",
                    "--packages-path",
                    directory,
                ]
            )

    def test_filter_duplicates(self):
        """Filter out duplicate requests, if the user provides any."""
        raise ValueError()

    def test_rxt(self):
        """Allow the user to pass a .rxt file, for a raw set of package requests."""

        def _is_failure_condition(context):
            return context.get_resolved_package("bar") is not None

        directory = os.path.join(_TESTS, "simple_packages")

        request_1 = _to_context_file("foo==1.0.0", packages_path=[directory])
        request_2 = _to_context_file("foo==1.1.0", packages_path=[directory])
        request_3 = _to_context_file("foo==1.2.0 bar==1.0.0", packages_path=[directory])

        with _patch_run(_is_failure_condition):
            result = _run_test(
                [
                    "run",
                    "",
                    request_1,
                    request_2,
                    request_3,
                    "--packages-path",
                    directory,
                ]
            )

        self.assertEqual(2, result.first_bad)


class CasePositioning(unittest.TestCase):
    """Make sure, no matter how many :ref:`contexts` are given, the results are okay."""

    def test_three(self):
        """Including a Rez package family creates some kind of issue."""

        def _is_failure_condition(context):
            return context.get_resolved_package("bar") is not None

        directory = os.path.join(_TESTS, "simple_packages")

        request_1 = "foo==1.0.0"
        request_2 = "foo==1.1.0"
        request_3 = "foo==1.2.0 bar==1.0.0"

        with _patch_run(_is_failure_condition):
            result = _run_test(
                [
                    "run",
                    "",
                    request_1,
                    request_2,
                    request_3,
                    "--packages-path",
                    directory,
                ]
            )

        self.assertEqual(2, result.first_bad)

    def test_permutations(self):
        """Including a Rez package family creates some kind of issue."""

        def _quick_test(expected, maximum=20):
            for count in range(2, maximum):
                if count - 1 < expected:
                    continue

                result = _build_bad_index_case(expected, count)
                self.assertEqual(
                    expected,
                    result,
                    msg='Count "{count}" expected "{expected}" but got "{result}" '
                    "result.".format(count=count, expected=expected, result=result),
                )

        _quick_test(1)
        _quick_test(4)
        _quick_test(10)
        _quick_test(14)
        _quick_test(17)
        _quick_test(19)


class InvalidRequests(unittest.TestCase):
    """Ensure start / end contexts and others work as expected."""

    def test_end_001(self):
        """Fail if the end request fails to resolve."""

        def _is_failure_condition(context):
            return str(context.get_resolved_package("foo").version) == "1.0.0"

        directory = os.path.join(_TESTS, "simple_packages")

        with _patch_run(_is_failure_condition), self.assertRaises(exception.BadRequest):
            _run_test(
                [
                    "run",
                    "",
                    "foo==1.0.0",
                    "foo==1.1.0 !foo-1",
                    "--packages-path",
                    directory,
                    "--partial",
                ]
            )

    def test_end_002(self):
        """Fail if the end request does not have the script issue."""

        def _is_failure_condition(context):
            return str(context.get_resolved_package("foo").version) == "1.1.0"

        directory = os.path.join(_TESTS, "simple_packages")

        with _patch_run(_is_failure_condition):
            with self.assertRaises(exception.BadRequest):
                _run_test(
                    [
                        "run",
                        "",
                        "/does/not/exist.rxt",
                        "foo==1.0.0",
                        "foo==1.1.0",
                        "--packages-path",
                        directory,
                    ]
                )

    def test_start_001(self):
        """Fail if the start request fails to resolve."""

        def _is_failure_condition(context):
            return str(context.get_resolved_package("foo").version) == "1.0.0"

        directory = os.path.join(_TESTS, "simple_packages")

        with _patch_run(_is_failure_condition), self.assertRaises(exception.BadRequest):
            _run_test(
                [
                    "run",
                    "",
                    "foo==1.0.0 !foo==1.0.0",
                    "foo==1.1.0",
                    "--packages-path",
                    directory,
                    "--partial",
                ]
            )

    def test_start_002(self):
        """Fail if the start request has the script issue."""

        def _is_failure_condition(context):
            return str(context.get_resolved_package("foo").version) == "1.0.0"

        directory = os.path.join(_TESTS, "simple_packages")

        with _patch_run(_is_failure_condition):
            with self.assertRaises(exception.BadRequest):
                _run_test(
                    [
                        "run",
                        "",
                        "/does/not/exist.rxt",
                        "foo==1.0.0",
                        "foo==1.1.0",
                        "--packages-path",
                        directory,
                    ]
                )


class Invalids(unittest.TestCase):
    """Check for user input or general issue cases.

    These unittests are to make the user's' experience in the :ref:`rez_bisect`
    CLI better. They don't serve any other purpose.

    """

    def test_missing_context(self):
        """Fail early if a :ref:`.rxt` file is given but the file does not exist."""

        def _is_failure_condition(context):
            return False

        directory = os.path.join(_TESTS, "simple_packages")

        with _patch_run(_is_failure_condition):
            with self.assertRaises(exception.BadRequest):
                _run_test(
                    [
                        "run",
                        "",
                        "/does/not/exist.rxt",
                        "foo==1.1.0",
                        "--packages-path",
                        directory,
                        "--partial",
                    ]
                )

    def test_same_contexts(self):
        """Fail early if the start and end are the same Rez :ref:`request`."""

        def _is_failure_condition(context):
            return False

        directory = os.path.join(_TESTS, "simple_packages")

        with _patch_run(_is_failure_condition):
            with self.assertRaises(exception.DuplicateContexts):
                _run_test(
                    [
                        "run",
                        "/does/not/exist.sh",
                        "foo==1.0.0",
                        "foo==1.0.0",
                        "--packages-path",
                        directory,
                        "--partial",
                    ]
                )

    def test_script_not_executable(self):
        """Fail if the script cannot be executed."""
        # By default, created Python files aren't executable
        path = _make_temporary_file("_not_executable.sh")

        with self.assertRaises(exception.PermissionsError):
            _run_test(["run", path, "foo==1.0.0", "foo==1.1.0", "foo==1.2.0"])

    def test_script_not_found(self):
        """Fail early if the script file doesn't exist."""
        with self.assertRaises(exception.FileNotFound):
            _run_test(
                ["run", "/does/not/exist.sh", "foo==1.0.0", "foo==1.1.0", "foo==1.2.0"]
            )

    def test_only_one_context_given(self):
        """Fail if only one Rez :ref:`context` is given."""

        def _is_failure_condition(context):
            return False

        directory = os.path.join(_TESTS, "simple_packages")

        with _patch_run(_is_failure_condition):
            with self.assertRaises(exception.UserInputError):
                _run_test(
                    [
                        "run",
                        "/does/not/exist.sh",
                        "foo==1.0.0",
                        "--packages-path",
                        directory,
                    ]
                )

    def test_two_contexts_but_no_partial_flag_enabled(self):
        """Don't allow two contexts to be compared unless :ref:`--partial` is added."""

        def _is_failure_condition(_):
            return False

        directory = os.path.join(_TESTS, "simple_packages")

        command = [
            "run",
            "/does/not/exist.sh",
            "foo==1.0.0",
            "foo==1.1.0",
            "--skip-end-check",
            "--packages-path",
            directory,
        ]

        with _patch_run(_is_failure_condition), self.assertRaises(exception.UserInputError):
            _run_test(command)

        with _patch_run(_is_failure_condition), mock.patch("rez_bisect.core.runner.bisect"):
            _run_test(command + ["--partial"])


class Options(unittest.TestCase):
    """Make sure :ref:`rez_bisect run` CLI flags work as expected."""

    def test_skip_end_check(self):
        """Let the user not check the end context and just end bisecting."""

        def _is_failure_condition(context):
            return str(context.get_resolved_package("foo").version) == "1.1.0"

        directory = os.path.join(_TESTS, "simple_packages")

        with _patch_run(_is_failure_condition):
            with mock.patch("rez_bisect.core.runner.bisect"):
                _run_test(
                    [
                        "run",
                        "",
                        "foo==1.0.0",
                        "foo==1.1.0",
                        "--packages-path",
                        directory,
                        "--skip-end-check",
                        "--partial",
                    ]
                )

    def test_skip_start_check(self):
        """Let the user not check the start context and just start bisecting."""

        def _is_failure_condition(context):
            return str(context.get_resolved_package("foo").version).startswith("1")

        directory = os.path.join(_TESTS, "simple_packages")

        with _patch_run(_is_failure_condition):
            with mock.patch("rez_bisect.core.runner.bisect"):
                _run_test(
                    [
                        "run",
                        "",
                        "foo==1.0.0",
                        "foo==1.1.0",
                        "--partial",
                        "--packages-path",
                        directory,
                        "--skip-start-check",
                    ]
                )

    def test_warn_intermediary_check(self):
        """Warn if one of the middle :ref:`contexts` cannot be resolved.

        See Also:
            :meth:`ContextInputs.test_failed_intermediary_context`

        """
        #  - If one of the resolve request steps has a conflict, skip it and go compare against the next one

        def _is_failure_condition(context):
            return str(context.get_resolved_package("foo").version) > _VERSION_1_1

        directory = os.path.join(_TESTS, "simple_packages")

        with _patch_run(_is_failure_condition), mock.patch("rez_bisect.cli._report_context_indices"):
            _run_test(
                [
                    "run",
                    "",
                    "foo==1.0.0",
                    "foo==1.1.0 !foo-1",
                    "foo==1.1.1 !foo-1",
                    "foo==1.1.0",
                    "foo==1.2.0",
                    "--packages-path",
                    directory,
                    "--skip-failed-contexts",
                ]
            )


class Reporting(unittest.TestCase):
    """Make sure the CLI prints the text that we expect."""

    def test_normal(self):
        """Make sure the base report looks as expected."""
        raise ValueError()

    def test_partial(self):
        """Make sure the report is adapted if :ref:`--partial` is included."""
        raise ValueError()


def _build_bad_index_case(bad_index, count):
    """Create a series of requests that are "good" until ``bad_index``.

    Args:
        bad_index (int):
            A 0-or-more number indicating the first index which has some kind
            of problem.
        count (int):
            A 1-or-more number indicating the number of total number of
            requests to include for the test.

    Returns:
        int:
            The first index where some issue was found. It should be the same
            as ``bad_index``.

    """

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
    command.extend(["--packages-path", directory, "--partial"])

    with _patch_run(_is_failure_condition):
        result = _run_test(command)

    return result.first_bad


def _make_temporary_file(suffix):
    """Make a temporary file and schedule it to be deleted later.

    Args:
        suffix (str):
            A unique name + file extension to use for the temporary file. e.g.
            ``"_some_label.rxt"``.

    Returns:
        str: The absolute path to the created file.

    """
    _, path = tempfile.mkstemp(suffix=suffix)
    atexit.register(functools.partial(os.remove, path))

    return path


@contextlib.contextmanager
def _patch_run(checker):
    """Force :ref:`rez_bisect run` to use a custom ``checker`` function.

    Args:
        checker (callable[rez.resolved_context.Context] -> bool):
            A function that returns True if some kind of issue is found or
            False, if the context is "valid".

    Yields:
        A temporary context where ``checker`` is enforced during bisecting.

    """

    with mock.patch("rez_bisect.cli._validate_script"), mock.patch(
        "rez_bisect.core.rez_helper.to_script_runner",
        wraps=checker,
    ) as patch:
        patch.return_value = checker

        yield


def _run_test(command):
    """Convert and run ``command`` as if it were written into the CLI.

    Args:
        command (list[str] or str):
            A raw :ref:`rez_bisect run` command,
            e.g. ``"run /some/executable.sh /a/context.rxt /another/context.rxt"``.

    Returns:
        object: Whatever the return value of the sub-parser is, if anything.

    """
    if isinstance(command, six.string_types):
        command = shlex.split(command)

    namespace = cli.parse_arguments(command)

    return cli.run(namespace)


def _to_context_file(request, packages_path=tuple()):
    """Make a raw Rez :ref:`request` into a :ref:`.rxt` file.

    Args:
        request (str):
            A raw Rez request, e.g. ``"foo-1+<2"``.
        packages_path (list[str], optional):
            The paths used to search for Rez packages while resolving.
            If no paths are given, the default paths are used instead.

    Returns:
        str: An absolute path to a generated :ref:`.rxt` file.

    """
    context = resolved_context.ResolvedContext(
        package_requests=rez_helper.to_request_list(request),
        package_paths=packages_path,
    )

    path = _make_temporary_file("_to_context_file.rxt")
    context.save(path)

    return path
