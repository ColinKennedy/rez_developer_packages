import argparse
import logging
import os

from rez.config import config

from .core import cli_helper, exception, path_helper, rez_helper, runner

_LOGGER = logging.getLogger(__name__)


def _run(namespace):
    current_directory = os.getcwd()

    script = path_helper.normalize(namespace.script, current_directory)
    _LOGGER.debug('Found script "%s".', script)
    _validate_script(script)

    requests = rez_helper.normalize_requests(namespace.requests, current_directory)
    contexts = rez_helper.to_contexts(requests, packages_path=namespace.packages_path)
    script_runner = rez_helper.to_script_runner(script)
    runner.bisect(script_runner, contexts)

    raise ValueError()


def _set_up_runner(sub_parsers):
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
        "--packages-path",
        default=config.packages_path,
        action=cli_helper.SplitPaths,
        help="The paths to check within for Rez packages.",
    )

    # # TODO : Add support for this argument
    # parser.add_argument("--partial", help="Guess the issue found between 2 resolves.")


def _validate_script(path):
    if os.path.isfile(path):
        return

    raise exception.FileNotFound('Script "{script}" does not exist on-disk.'.format(script=script))


def parse_arguments(text):
    parser = argparse.ArgumentParser(description="Check Rez resolves for a specific issue.")
    sub_parsers = parser.add_subparsers(help="All available commands.")

    _set_up_runner(sub_parsers)

    return parser.parse_args(text)


def run(namespace):
    namespace.execute(namespace)


def main(text):
    """Run the main execution of the script."""
    # TODO : Add verbose logger handling
    namespace = parse_arguments(text)
    run(namespace)
