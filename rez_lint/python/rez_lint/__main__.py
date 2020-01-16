#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The main entry point for ``rez_lint``. This module controls the CLI program."""

from __future__ import print_function

import argparse
import importlib
import itertools
import logging
import operator
import os
import sys

from . import cli
from .core import message_description, registry
from .plugins.checkers import (
    base_checker,
    conventions,
    dangers,
    explains,
    explains_comment,
)
from .plugins.contexts import base_context, packaging, parsing

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


def _register_internal_plugins():
    """Add the plugins that ``rez_lint`` offers by default to the user.

    This function must run before :func:`_register_external_plugins` so
    that it has a chance to override the plugins created here.

    """
    registry.register_checker(conventions.SemanticVersioning)
    registry.register_checker(dangers.ImproperRequirements)
    registry.register_checker(dangers.MissingRequirements)
    registry.register_checker(dangers.NoRezTest)
    registry.register_checker(dangers.NotPythonDefinition)
    registry.register_checker(dangers.RequirementLowerBoundsMissing)
    registry.register_checker(dangers.RequirementsNotSorted)
    registry.register_checker(dangers.TooManyDependencies)
    registry.register_checker(dangers.UrlNotReachable)
    registry.register_checker(explains.NoChangeLog)
    registry.register_checker(explains.NoDocumentation)
    registry.register_checker(explains.NoReadMe)
    registry.register_checker(explains_comment.NeedsComment)
    registry.register_context(packaging.HasPythonPackage)
    registry.register_context(packaging.SourceResolvedContext)
    registry.register_context(parsing.ParsePackageDefinition)


def _register_external_plugins():
    """Add user plugins to the current ``rez_lint`` environment.

    If any user added their own context or checker plugins, this
    function will add them here.

    """
    environment = os.getenv("REZ_LINT_PLUGIN_PATHS")

    if not environment:
        _LOGGER.debug('No environment paths were "%s" found.')

        return

    _LOGGER.debug('Environment paths "%s" found.', environment)

    paths = []

    for namespace in environment.split(os.pathsep):
        if namespace not in paths:
            paths.append(namespace)

    for namespace in paths:
        _LOGGER.info('Importing module "%s".', namespace)
        importlib.import_module(namespace)

    registry.register_plugins(
        itertools.chain(
            base_checker.BaseChecker.__subclasses__(),
            base_context.BaseContext.__subclasses__(),
        )
    )


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
    _register_internal_plugins()
    _register_external_plugins()

    arguments = _parse_arguments(sys.argv[1:])
    folder, disable = _resolve_arguments(arguments)

    descriptions = cli.lint(
        folder,
        disable=disable,
        recursive=arguments.recursive,
        verbose=arguments.verbose,
    )

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
