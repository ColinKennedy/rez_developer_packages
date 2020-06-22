#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""A thin wrapper around "filer.py" that automatically builds / symlinks Rez packages."""

from __future__ import print_function

import argparse
import os
import sys

from . import exceptions, filer


def _parse_arguments(text):
    """Create arguments for building file(s)/folder(s) of a Rez package.

    Args:
        text (list[str]):
            The user-provided text from command-line. This is usually
            space-separated text.

    Returns:
        :class:`argparse.Namespace`: The parsed user-provided text.

    """
    parser = argparse.ArgumentParser(
        description="Build Python-based Rez packages in just a single command.",
    )

    parser.add_argument(
        "-i",
        "--items",
        nargs="+",
        help="The relative paths to each file/folder to copy / install.",
    )

    parser.add_argument(
        "-e",
        "--eggs",
        nargs="+",
        help="The relative paths to each file/folder to make into a .egg file.",
    )

    parser.add_argument(
        "-s",
        "--symlink",
        action="store_true",
        help="If True, symlink back to the source Rez package, instead of creating new files.",
    )

    known, _ = parser.parse_known_args(text)

    return known


def main(text):
    """Run the main execution of the current script."""
    arguments = _parse_arguments(text)

    try:
        filer.build(
            os.environ["REZ_BUILD_SOURCE_PATH"],
            os.environ["REZ_BUILD_INSTALL_PATH"],
            items=arguments.items,
            eggs=arguments.eggs,
        )
    except exceptions.NonRootItemFound as error:
        print(error, file=sys.stderr)
        print("Please check spelling and try again.")


if __name__ == "__main__":
    main(sys.argv[1:])
