#!/usr/bin/env python

"""The module which `__main__.py` uses in order to do any bisect-related work."""

import argparse
import operator

from .core import rez_helper, runner_


def _runner(arguments):
    """Run a bisect, using some automated command.

    Args:
        arguments (:class:`argparse.Namespace`): The parser user input to call.

    """
    good = rez_helper.to_context(arguments.good)
    bad = rez_helper.to_context(arguments.bad)

    found = runner_.bisect(good, bad, arguments.command)

    print("These added / removed / changed packages are the cause of the issue:")

    for key, packages in runner_.summarize(good, found).items():
        print("    {key}".format(key=key))

        for package in sorted(packages, key=operator.attrgetter("name")):
            print("        {package.name}-{package.version}".format(package=package))


def _parse_arguments(text):
    """Parse the user's input.

    Args:
        text (iter[str]):
            The text coming from the user's shell. This command
            is space-separated. e.g. `["run /tmp/context.rxt",
            "/tmp/checker.sh"]`.

    Returns:
        :class:`argparse.Namespace`: The parsed user content.

    """
    parser = argparse.ArgumentParser(
        description="Check Rez resolves for a specific issue."
    )
    subparsers = parser.add_subparsers(help="All available commands.")

    runner = subparsers.add_parser(
        "run", help="Auto-find the issue, using a pre-defined command."
    )
    runner.add_argument("good", help="A Rez context which does not contain the issue.")
    runner.add_argument("bad", help="A Rez context which contains the issue.")
    runner.add_argument(
        "command", help="The command to run in each resolve, to check for some issue."
    )
    runner.set_defaults(execute=_runner)

    return parser.parse_args(text)


def main(text):
    """Parse the user's input and run some command.

    Args:
        text (iter[str]):
            The text coming from the user's shell. This command
            is space-separated. e.g. `["run /tmp/context.rxt",
            "/tmp/checker.sh"]`.

    """
    arguments = _parse_arguments(text)
    arguments.execute(arguments)