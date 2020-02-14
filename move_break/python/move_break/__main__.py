#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The main module that deals with command-line specific data."""

import argparse
import os
import sys

from .core import import_registry
from . import cli

_CURRENT_DIRECTORY = os.path.dirname(os.path.realpath(__file__))


def _parse_arguments(text):
    """Split the user-provided text into Python objects.

    Args:
        text (list[str]): The arguments that need to be parsed and returned.

    Returns:
        :class:`argparse.Namespace`:
            The parsed output. At minimum, it needs to return paths of
            folders or Python files to change plus old / new namespaces.

    """
    # TODO : Change this to allow 1+ paths (multiple paths at once)
    parser = argparse.ArgumentParser(
        description="Replace any Python imports in a file or directory. It's useful for refactoring"
    )

    parser.add_argument("path", help="A file or folder to replace Python imports.")
    parser.add_argument(
        "namespaces", help="A comma-separated list of old and new namespaces."
    )
    parser.add_argument(
        "-p",
        "--partial-matches",
        action="store_true",
        help="If an import brings in multiple namespaces at a time, ""the user-provided namespaces don't need to match all of the import.",
    )

    parser.add_argument(
        "-a",
        "--aliases",
        action="store_true",
        help="If enabled, add the old namespace as an alias to the new namespace, if needed.",
    )

    parser.add_argument(
        "-r",
        "--replace",
        action="store_true",
        help="If enabled, replace imports in the rest of the file, not just the import statements.")

    parser.add_argument(
        "-t",
        "--types",
        choices=import_registry.get_plugin_types(),
        help="A comma-separated list of allowed import statements to replace.",
    )

    return parser.parse_args(text)


def _expand_namespaces(text):
    """Process the comma-separated namespaces into a list of "old" and "new" namespaces.

    Args:
        text (iter[str]): The lines of namespaces that need to be adjusted.

    Returns:
        set[tuple[str, str]]:
            Each pair represents a namespace import to search for and
            the namespace that it will be replaced with.

    """
    output = set()

    for line in text:
        old, new = line.split(",")
        output.add((old, new))

    return output


def _expand_paths(path):
    """Find every Python file in `path`.

    Args:
        path (str): An absolute or relative path to a Python file or folder on-disk.

    Raises:
        ValueError: If `path` is not a valid file or folder on-disk.

    Returns:
        set[str]: The found Python files.

    """
    if not os.path.isabs(path):
        path = os.path.normpath(os.path.join(_CURRENT_DIRECTORY, path))

    if not os.path.exists(path):
        raise ValueError('Path "{path}" is not a file or folder.'.format(path=path))

    if os.path.isfile(path):
        return {path}

    files = set()

    for root, files, _ in os.walk(path):
        for path_ in files:
            if not path_.endswith(".py"):
                files.add(os.path.join(root, path_))

    return files


def main():
    """Run the main execution of the current script."""
    arguments = _parse_arguments(sys.argv[1:])
    paths = _expand_paths(arguments.path)
    namespaces = _expand_namespaces(arguments.namespace)

    cli.run(paths, namespaces, partial=arguments.partial_matches)


if __name__ == "__main__":
    main()
