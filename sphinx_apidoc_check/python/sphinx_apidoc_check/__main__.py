#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The entry point for the ``sphinx_apidoc_check`` CLI script."""

from __future__ import print_function

import argparse
import shlex
import sys

from . import cli
from .core import check_constant, check_exception


def _parse_arguments(text):
    """Split raw user input into tokenized Python objects.

    Args:
        text (str):
            Some user input from command-line. Usually something like
            '"python --output-dir documentation/source/api" --no-strict".

    Returns:
        :class:`argparse.Namespace`: The parsed arguments.

    """
    parser = argparse.ArgumentParser(
        description="A CI linter that checks if API documentation needs to be re-generated.",
    )

    parser.add_argument(
        "command",
        help="The exact ``sphinx-apidoc`` call that will be used to write API documentation.",
    )

    parser.add_argument(
        "-n",
        "--no-strict",
        action="store_true",
        help="If this flag is added, old files in the output directory that don't point "
        "to source Python files are allowed. Otherwise, they must be removed.",
    )

    parser.add_argument(
        "-d",
        "--directory",
        help="The folder on-disk that will be cd'ed into before running the "
        "``sphinx-apidoc`` comnand.",
    )

    return parser.parse_args(text)


def main(text):
    """Run the main execution of the current script."""
    arguments = _parse_arguments(text)

    try:
        to_add, to_skip, to_remove = cli.check(
            shlex.split(arguments.command), directory=arguments.directory,
        )
    except check_exception.CoreException as error:
        print(error, file=sys.stderr)

        sys.exit(check_constant.ERROR_ENCOUNTERED)

    if to_add:
        print("These files must be added:")

        for path in sorted(to_add):
            print(path)

    has_remove_issues = not arguments.no_strict and to_remove

    if has_remove_issues:
        print()
        print("These files must be removed:")

        for path in sorted(to_remove):
            print(path)

    if to_add or has_remove_issues:
        print()
        print("Please re-run sphinx-apidoc to fix this")

        sys.exit(check_constant.UPDATE_CODE)

    print("These files will remain unchanged (no action required):")

    for path in sorted(to_skip):
        print(path)

    print()
    print("Everything looks good. No further action needed")

    sys.exit(0)


if __name__ == "__main__":
    main(sys.argv[1:])
