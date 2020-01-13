#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""A thin wrapper around "filer.py" that automatically builds / symlinks Rez packages."""

import argparse
import os
import sys

from . import filer


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
        "-s",
        "--symlink",
        action="store_true",
        help="If True, symlink back to the source Rez package, instead of creating new files.",
    )

    return parser.parse_args(text)


def main(text):
    """Run the main execution of the current script."""
    arguments = _parse_arguments(text)

    filer.build(
        os.environ["REZ_BUILD_SOURCE_PATH"],
        os.environ["REZ_BUILD_INSTALL_PATH"],
        arguments.items,
    )


if __name__ == "__main__":
    main(sys.argv[1:])
