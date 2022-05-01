"""Miscellaneous functions to make unittests more concise."""

import contextlib
import shlex

import six
from python_compatibility import wrapping
from six.moves import mock

from rez_bisect import cli


@contextlib.contextmanager
def patch_run(checker):
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


def run_test(command):
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

    with wrapping.silence_printing():
        return cli.run(namespace)
