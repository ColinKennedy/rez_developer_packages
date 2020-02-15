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
        default="",
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

    for line in text.splitlines():
        try:
            old, new = line.split(",")
        except ValueError:
            raise ValueError(
                'Text "{text}" needs to have a comma to '
                'separate the old and new namespace. Got "{line}".'
                ''.format(text=text, line=line)
            )

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

    output = set()

    for root, _, files in os.walk(path):
        for path_ in files:
            if path_.endswith(".py"):
                output.add(os.path.join(root, path_))

    return output


def _expand_types(text):
    return set(filter(None, text.split(",")))


def main():
    """Run the main execution of the current script."""
    arguments = _parse_arguments(sys.argv[1:])
    paths = _expand_paths(arguments.path)
    namespaces = _expand_namespaces(arguments.namespaces)
    import_types = _expand_types(arguments.types)
    allowed_import_types = choices=import_registry.get_plugin_types()
    remaining_types = import_types - allowed_import_types

    if remaining_types:
        raise ValueError(
            'Types "{remaining_types}" are not valid. '
            'Allowed types are "{allowed_import_types}".'
            ''.format(remaining_types=remaining_types, allowed_import_types=allowed_import_types))

    cli.move_imports(
        paths,
        namespaces,
        partial=arguments.partial_matches,
        import_types=arguments.types,
    )


if __name__ == "__main__":
    main()
