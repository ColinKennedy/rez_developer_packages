#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Parse the user's input from the CLI and run a `rez-env` command using it."""

import argparse

from .core import environment


def _parse_arguments(text):
    """Split the user's request into the Rez package + Rez test(s).

    Args:
        text (list[str]):
            The space-separated input from the CLI. Usually from :obj:`sys.argv`.

    Returns:
        :class:`argparse.Namespace`: The parsed arguments.

    """
    parser = argparse.ArgumentParser(description="")

    parser.add_argument(
        "package_request", help="The Rez package to make an environment for."
    )
    parser.add_argument(
        "tests",
        nargs="*",
        help="The test requirements to append to the package request.",
    )

    return parser.parse_args(text)


def main(text):
    """Split the user's request into the Rez package + Rez test(s).

    Args:
        text (list[str]):
            The space-separated input from the CLI. Usually from :obj:`sys.argv`.

    """
    arguments = _parse_arguments(text)
    environment.run(arguments.package_request, arguments.tests)
