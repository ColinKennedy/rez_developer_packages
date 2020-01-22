#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The main entry point for ``rez_lint``. This module controls the CLI program."""

from __future__ import print_function

import argparse
import itertools
import logging
import operator
import os
import sys

from . import cli
from .core import exceptions, exit_code, message_description

_LOGGER = logging.getLogger("rez_lint")
__HANDLER = logging.StreamHandler(stream=sys.stdout)
__FORMATTER = logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")
__HANDLER.setFormatter(__FORMATTER)
_LOGGER.addHandler(__HANDLER)


def _parse_arguments(text):
    """Tokenize the user's input to command-line into something that this package can use.

    Args:
        text (str): The raw user input from the terminal.

    Returns:
        :class:`argparse.Namespace`: The parsed values.

    """
    parser = argparse.ArgumentParser(description="Check a Rez package for issues.",)

    parser.add_argument(
        "-d",
        "--disable",
        default="",
        help="A comma-separated list of codes to not check.",
    )

    parser.add_argument(
        "-f",
        "--folder",
        default=".",
        help="The starting point that will be used to search for Rez package(s). "
        "This defaults to the current directory.",
    )

    parser.add_argument(
        "-r",
        "--recursive",
        action="store_true",
        help="Enable this flag to search for all Rez packages under the given --folder.",
    )

    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Add this option to get more information about a check result.",
    )

    parser.add_argument(
        "-g",
        "--vimgrep",
        action="store_true",
        help="Output check results with path, line, and column information. "
        "When enabled, this option will disable --verbose.",
    )

    return parser.parse_args(text)


def _resolve_arguments(arguments):
    """Find the disabled user rules.

    Args:
        arguments (:class:`argparse.Namespace`): The parsed user input.

    Returns:
        tuple[str, set[str]]:
            The absolute folder where to search for Rez package(s) and
            every issue code that will be ignored from the final report.

    """
    rules = (rule.lstrip() for rule in arguments.disable.split(","))
    rules = set(filter(None, rules))

    folder = arguments.folder

    if not os.path.isabs(folder):
        folder = os.path.normpath(os.path.join(os.getcwd(), folder))

    return folder, rules


def main():
    """Run the main execution of the current script."""
    arguments = _parse_arguments(sys.argv[1:])
    folder, disable = _resolve_arguments(arguments)

    try:
        descriptions = cli.lint(
            folder,
            disable=disable,
            recursive=arguments.recursive,
            verbose=arguments.verbose,
        )
    except exceptions.NoPackageFound as error:
        print(str(error), file=sys.stderr)

        sys.exit(exit_code.NO_REZ_PACKAGE)

    if not descriptions:
        if not arguments.vimgrep:
            print("No issues were found. Everything looks good!")

        sys.exit(0)

    lines = []
    padding_column = max(
        description.get_padding_column()
        for description in descriptions
        if description.is_location_specific()
    )
    padding_row = max(
        description.get_padding_row()
        for description in descriptions
        if description.is_location_specific()
    )

    for header, descriptions in itertools.groupby(
        descriptions, operator.methodcaller("get_header")
    ):
        if not arguments.vimgrep:
            lines.append("************* " + header)

        for description in descriptions:
            if arguments.vimgrep:
                # Note: when vimgrep is enabled, not every item will be printed
                if description.is_location_specific():
                    lines.append(description.get_location_data())
            else:
                lines.extend(
                    description.get_message(
                        verbose=arguments.verbose,
                        padding=[padding_row, padding_column],
                    )
                )

    if arguments.vimgrep:
        # Make sure that each file + row / column prints in ascending order
        lines = sorted(lines, key=message_description.get_vimgrep_sort)

    for line in lines:
        print(line)

    if not arguments.vimgrep:
        print()
        print("Issues were found. Please fix them and re-run.")

    sys.exit(1)


main()
