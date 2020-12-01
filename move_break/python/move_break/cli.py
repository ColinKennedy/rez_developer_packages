#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The main module that deals with command-line specific data."""

import argparse
import collections
import os

from . import finder, mover
from .core import import_registry

_CURRENT_DIRECTORY = os.path.dirname(os.path.realpath(__file__))
Configuration = collections.namedtuple(
    "Configuration",
    "paths namespaces partial_matches types aliases continue_on_syntax_error",
)


def _parse_arguments(text):
    """Split the user-provided text into Python objects.

    Args:
        text (list[str]): The arguments that need to be parsed and returned.

    Returns:
        :class:`argparse.Namespace`:
            The parsed output. At minimum, it needs to return paths of
            folders or Python files to change plus old / new namespaces.

    """
    parser = argparse.ArgumentParser(
        description="Replace any Python imports in a file or directory. It's useful for refactoring"
    )

    parser.add_argument(
        "paths", nargs="+", help="A file or folder to replace Python imports."
    )
    parser.add_argument(
        "namespaces", help="A comma-separated list of old and new namespaces."
    )
    parser.add_argument(
        "-p",
        "--partial-matches",
        action="store_true",
        help="If an import brings in multiple namespaces at a time, "
        "the user-provided namespaces don't need to match all of the import.",
    )

    parser.add_argument(
        "-a",
        "--aliases",
        action="store_true",
        help="If enabled, add the old namespace as an alias to the new namespace, if needed.",
    )

    parser.add_argument(
        "-t",
        "--types",
        default="",
        help="A comma-separated list of allowed import statements to replace.",
    )

    parser.add_argument(
        "-c",
        "--continue-on-syntax-error",
        action="store_true",
        help="If one or more discovered files has a syntax errors, "
        "don't modify it or exit the script.",
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

    for line in text.split(":"):
        try:
            old, new = line.split(",")
        except ValueError:
            raise ValueError(
                'Text "{text}" needs to have a comma to '
                'separate the old and new namespace. Got "{line}".'
                "".format(text=text, line=line)
            )

        output.add((old, new))

    return output


def _expand_types(text):
    """Split `text`, a comma-separated string, into unique, non-empty strings."""
    return set(filter(None, text.split(",")))


def parse_arguments(text):
    """Convert user-provided CLI text into something that `move_break` can run with.

    Args:
        text (list[str]):
            The user-provided tokens from command-line. It's the user's
            raw input but split by-spaces.

    Raises:
        ValueError: If the user gives an unsupported import type.

    Returns:
        :attr:`move_break.cli.Configuration`:
            A fully parsed and clean user input. This object provides
            all the arguments needed to call :func:`.move_imports`.

    """
    arguments = _parse_arguments(text)
    paths = set()

    fallback_directory = os.getcwd()

    for path in arguments.paths:
        paths.update(finder.expand_paths(path, fallback_directory))

    namespaces = _expand_namespaces(arguments.namespaces)
    import_types = _expand_types(arguments.types)
    allowed_import_types = import_registry.get_plugin_types()
    remaining_types = import_types - allowed_import_types

    if remaining_types:
        raise ValueError(
            'Types "{remaining_types}" are not valid. '
            'Allowed types are "{allowed_import_types}".'
            "".format(
                remaining_types=remaining_types,
                allowed_import_types=allowed_import_types,
            )
        )

    return Configuration(
        paths,
        namespaces,
        arguments.partial_matches,
        arguments.types,
        arguments.aliases,
        arguments.continue_on_syntax_error,
    )


def main(text):
    """Run the main execution of the current script.

    Args:
        text (list[str]):
            The user-provided tokens from command-line. It's the user's
            raw input but split by-spaces.

    Returns:
        set[str]: The Python modules that were actually overwritten.

    """
    configuration = parse_arguments(text)

    return mover.move_imports(
        configuration.paths,
        configuration.namespaces,
        partial=configuration.partial_matches,
        import_types=configuration.types,
        aliases=configuration.aliases,
        continue_on_syntax_error=configuration.continue_on_syntax_error,
    )
