"""The main work module for the :ref:`rez_bisect cli`."""

import argparse
import logging
import os

from rez.config import config

from .core import cli_helper, exception, path_helper, rez_helper, runner

_LOGGER = logging.getLogger(__name__)


def _run(namespace):
    """Run an :ref:`automated Rez bisect`, in Rez.

    Raises:
        BadRequest:
            If ``namespace`` defines a start and end Rez :ref:`context` which
            is broken, the ensuing bisect will surely fail. Instead, we raise
            this exception beforehand, to let the user they need to change
            something.

    Returns:
        _BisectSummary: The bisect summary, serialized into text.

    """
    current_directory = os.getcwd()

    script = path_helper.normalize(namespace.script, current_directory)
    _LOGGER.debug('Found script "%s".', script)
    _validate_script(script)

    _validate_requests(namespace.requests, namespace.partial)
    contexts = rez_helper.to_contexts(
        namespace.requests,
        current_directory,
        packages_path=namespace.packages_path,
    )
    _validate_contexts(contexts)

    has_issue = rez_helper.to_script_runner(script)

    if not namespace.skip_start_check and has_issue(contexts[0]):
        raise exception.BadRequest(
            'Start context "{contexts[0]}" fails check, "{script}".'.format(
                contexts=contexts,
                script=script,
            )
        )

    if not namespace.skip_end_check and not has_issue(contexts[-1]):
        raise exception.BadRequest(
            'End context "{context}" does not fail check, "{script}".'.format(
                context=contexts[-1],
                script=script,
            )
        )

    return runner.bisect(has_issue, contexts)


def _set_up_runner(sub_parsers):
    """Add the :ref:`rez_bisect run` sub-parser to ``sub_parsers``.

    Args:
        sub_parsers (argparse._SubParsersAction):
            The nested parser group to add a new command into.

    """
    run = sub_parsers.add_parser("run", help="Checks for an issue, using a script.")
    run.set_defaults(execute=_run)

    run.add_argument(
        "script",
        help="A script which errors as soon as some issue is found.",
    )

    run.add_argument(
        "requests",
        nargs="+",
        help="Rez requests / resolves to check within for issues.",
    )

    run.add_argument(
        "--skip-end-check",
        action="store_true",
        help="If included, don't check the last context using ``script``.",
    )

    run.add_argument(
        "--skip-start-check",
        action="store_true",
        help="If included, don't check the first context using ``script``.",
    )

    run.add_argument(
        "--packages-path",
        default=config.packages_path,
        action=cli_helper.SplitPaths,
        help="The paths to check within for Rez packages.",
    )

    # TODO : Add support for this argument
    run.add_argument(
        "--partial",
        action="store_true",
        help="Guess the issue found between 2 resolves.",
    )


def _validate_contexts(contexts):
    """Ensure ``contexts`` are valid for running in the CLI.

    Args:
        contexts (list[rez.resolved_context.ResolvedContext]):
            The Rez requests, resolved as packages, to check.

    Raises:
        UserInputError: If not enough :ref:`contexts` were given.
        DuplicateContexts: If the start / end :ref:`contexts` are identical.

    """
    start = contexts[0]
    end = contexts[-1]

    if len(contexts) == 1:
        raise exception.UserInputError(
            "You must provide at least 2 Rez requests / contexts. "
            'We only got "{contexts}".'.format(contexts=contexts)
        )

    if start == end:
        raise exception.DuplicateContexts("Start and end context are the same.")


def _validate_requests(requests, partial=False):
    """Ensure ``requests`` are valid before converting them to :ref:`contexts`.

    Args:
        requests (iter[str]):
            Each :ref:`.rxt` resolve file or a raw request ``"foo-1+<2 bar==3.0.0"``
            to check.
        partial (bool, optional):
            If the user wants to bisect not just ``requests`` but the diff
            between the requests. When ``partial`` is True, this function will
            never raise an exception.

    Raises:
        UserInputError: If 2 contexts are given but ``partial`` is False.

    """
    if len(requests) != 2:
        return

    if partial:
        return

    raise exception.UserInputError(
        "You cannot compare only two contexts with adding --partial. "
        "Please either add more contexts or include the --partial flag."
    )


def _validate_script(path):
    """Ensure ``path`` exists on-disk.

    Args:
        path (str): An executable file to run, such as a .sh or .bat file.

    Raises:
        FileNotFound: If ``path`` doesn't exist on-disk.
        PermissionsError: If ``path`` exists but cannot be executed.

    """
    if not os.path.isfile(path):
        raise exception.FileNotFound(
            'Script "{path}" does not exist on-disk.'.format(path=path)
        )

    if not os.access(path, os.X_OK):
        raise exception.PermissionsError(
            'Script "{path}" is not executable.'.format(path=path)
        )


def parse_arguments(text):
    """Convert the user's CLI input to something :ref:`rez_bisect` can understand.

    Args:
        text (list[str]): The raw CLI input, separated by spaces. e.g. ``sys.argv[1:]``.

    Returns:
        argparse.Namespace: The parsed user text input.

    """
    parser = argparse.ArgumentParser(
        description="Check Rez resolves for a specific issue."
    )
    sub_parsers = parser.add_subparsers(help="All available commands.")

    _set_up_runner(sub_parsers)

    return parser.parse_args(text)


def run(namespace):
    """Execute the default function associated with the sub-parser in ``namespace``.

    Args:
        namespace (argparse.Namespace): The parsed user text input.

    Returns:
        object: Whatever the return value of the sub-parser is, if anything.

    """
    return namespace.execute(namespace)


def main(text):
    """Run the main execution of the script."""
    # TODO : Add verbose logger handling
    namespace = parse_arguments(text)
    run(namespace)
