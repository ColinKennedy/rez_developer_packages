#!/usr/bin/env python

import argparse

from .core import rez_helper, runner_



def _runner(arguments):
    bad = rez_helper.to_context(arguments.bad)
    good = None

    if arguments.good:
        good = rez_helper.to_context(arguments.good)

    runner_.run(bad, arguments.command, good=good)


def _parse_arguments(text):
    parser = argparse.ArgumentParser(description="Check Rez resolves for a specific issue.")
    subparsers = parser.add_subparsers(help="All available commands.")

    runner = subparsers.add_parser("run", help="Auto-find the issue, using a pre-defined command.")
    runner.add_argument("bad", help="A Rez context which contains the issue.")
    runner.add_argument("command", help="The command to run in each resolve, to check for some issue.")
    runner.add_argument("--good", help="A Rez context which does not contain the issue.")
    runner.set_defaults(execute=_runner)

    return parser.parse_args(text)


def main(text):
    arguments = _parse_arguments(text)
    arguments.execute(arguments)
