#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The main module that has almost all command-line specific logic."""

from __future__ import print_function

import argparse
import shlex
import sys

from .core import constants, linker


def _bake_from_request(arguments):
    """Generate symlinks for a user's given Rez package request.

    Args:
        arguments (:class:`argparse.Namespace`):
            The parsed user CLI data. It should contain "force" and
            "output_directory" and "request" as attributes.

    """
    request = shlex.split(arguments.request)

    try:
        linker.bake_from_request(request, arguments.output_directory, force=arguments.force)
    except ValueError:
        print('Request "{arguments.request}" contains one-or-more missing Rez packages.', sys.stderr)

        sys.exit(constants.CANNOT_BAKE_FROM_REQUEST)

def _bake_from_current_environment(arguments):
    """Generate symlinks to reproduce the current environment.

    Args:
        arguments (:class:`argparse.Namespace`):
            The parsed user CLI data. It should contain "force" and
            "output_directory" as attributes.

    """
    try:
        linker.bake_from_current_environment(
            arguments.output_directory, force=arguments.force
        )
    except EnvironmentError:
        print(
            "You are not in an Rez-resolved environment. Cannot bake the current environment.",
            sys.stderr,
        )

        sys.exit(constants.CANNOT_BAKE_FROM_CURRENT_ENVIRONMENT)


def _add_common_arguments(parser):
    """Add some arguments that all subparsers in rez_symbl must have.

    Args:
        parser (:class:`argparse.ArgumentsParser`):
            Some CLI text parser which will be modified by this function.

    """
    parser.add_argument(
        "-o",
        "--output-directory",
        required=True,
        help="The location on-disk where all of the symlinks will be created.",
    )
    parser.add_argument(
        "-f",
        "--force",
        action="store_true",
        help="Delete symlinks if they already exist",
    )


def _parse_arguments(text):
    """Split the user's arguments into valid Python objects.

    Args:
        text (list[str]):
            The raw CLI input (split by spaces e.g. using :func:`shlex.split` or :attr:`sys.argv`).

    Returns:
        :class:`argparse.Namespace`: The found user input.

    """
    parser = argparse.ArgumentParser(
        description="Bake A Rez resolve into an external directory"
    )
    subparsers = parser.add_subparsers(description="subparsers")

    bake_from_request = subparsers.add_parser("bake-from-request")
    bake_from_request.add_argument(
        "request",
        help="What you'd normally put in a rez-env command. e.g. `rez-env foo`",
    )
    _add_common_arguments(bake_from_request)
    bake_from_request.set_defaults(execute=_bake_from_request)

    bake_from_current_environment = subparsers.add_parser(
        "bake-from-current-environment"
    )
    _add_common_arguments(bake_from_current_environment)
    bake_from_current_environment.set_defaults(execute=_bake_from_current_environment)

    arguments = parser.parse_args(text)

    return arguments


def main(text):
    """Get the user's given command and process it. Add symlink as-needed.

    Args:
        text (list[str]):
            The raw CLI input (split by spaces e.g. using :func:`shlex.split` or :attr:`sys.argv`).

    """
    arguments = _parse_arguments(text)
    arguments.execute(arguments)
