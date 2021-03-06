#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""A thin wrapper around "filer.py" that automatically builds / symlinks Rez packages."""

from __future__ import print_function

import argparse
import os
import sys

from . import exceptions, filer, linker


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
        "--hdas",
        nargs="+",
        help="The relative paths to each folder containing VCS-style Houdini HDAs.",
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
        "--symlink",
        action="store_true",
        default=linker.must_symlink(),
        help="If True, symlink everything back to the source Rez package.",
    )

    parser.add_argument(
        "--symlink-files",
        action="store_true",
        default=linker.must_symlink_files(),
        help="If True, symlink files back to the source Rez package.",
    )

    parser.add_argument(
        "--symlink-folders",
        action="store_true",
        default=linker.must_symlink_folders(),
        help="If True, symlink folders back to the source Rez package.",
    )

    known, _ = parser.parse_known_args(text)

    return known


def main(text):
    """Run the main execution of the current script."""
    arguments = _parse_arguments(text)

    source = os.environ["REZ_BUILD_SOURCE_PATH"]
    destination = os.environ["REZ_BUILD_INSTALL_PATH"]

    filer.clean(destination)

    try:
        filer.build(
            source,
            destination,
            hdas=arguments.hdas,
            items=arguments.items,
            eggs=arguments.eggs,
            symlink=arguments.symlink,
            symlink_folders=arguments.symlink_folders,
            symlink_files=arguments.symlink_files,
        )
    except exceptions.NonRootItemFound as error:
        print(error, file=sys.stderr)
        print("Please check spelling and try again.")


if __name__ == "__main__":
    main(sys.argv[1:])
