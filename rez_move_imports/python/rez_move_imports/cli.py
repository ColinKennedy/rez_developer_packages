#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The main module that parses the user's CLI input so ``rez_move_imports`` can work."""

import argparse
import collections
import os
import shlex

from move_break import cli
from rez.vendor.version import requirement
from rez_utilities import inspection

from .core import replacer


def _parse_arguments(text):
    """Split the user-provided text into Python objects.

    Args:
        text (list[str]): The raw CLI input, split by spaces.

    Returns:
        :class:`argparse.Namespace`: The user's text, split into Python objects.

    """
    parser = argparse.ArgumentParser(
        description="Change a Rez package's imports and then bump the require Rez version(s)."
    )
    parser.add_argument("command", help="The full command to pass to move_break.")
    parser.add_argument(
        "-r",
        "--requirements",
        action="append",
        required=True,
        help="A package and namespace(s) to possibly add to the current Rez package.",
    )
    parser.add_argument(
        "-d",
        "--deprecate",
        action="append",
        required=True,
        help="A requirement of the current package and namespace(s) to possibly remove.",
    )
    parser.add_argument(
        "-u",
        "--use-pythonpath",
        action="store_true",
        help="Search for python files only within PYTHONPATH instead of the whole Rez package.",
    )
    parser.add_argument(
        "-p",
        "--package-directory",
        default=".",
        help="The path (relative to absolute) to the Rez package that will be modified.",
    )

    return parser.parse_args(text)


def _split_package_and_namespaces(package_and_namespaces):
    """Split a comma-separated list into non-empty sections.

    Args:
        package_and_namespaces (str):
            A Rez package definition + the Python
            dot-separated import namespaces.
            e.g. "some_package-2,some_package.import_namespace.here,another.one".

    Returns:
        list[str]: The split items.

    """
    parts = []

    for item in package_and_namespaces.split(","):
        item = item.strip()

        if item:
            parts.append(item)

    return parts


def _expand(items):
    """Group every Rez and Python dot-separated Python namespaces.

    Args:
        items (iter[str]):
            Each Rez package definition + the Python
            dot-separated import namespaces.
            e.g. ["some_package-2,some_package.import_namespace.here,another.one"].

    Returns:
        list[tuple[:class:`rez.vendor.version.requirement.Requirement`, set[str]]]:
            Each user-provided Rez package and Python dot-separated
            import namespaces that the user wants ``rez_move_imports``
            to remember during the execution of the CLI.

    """
    output = collections.defaultdict(set)

    for package_and_namespaces in items:
        parts = _split_package_and_namespaces(package_and_namespaces)
        package = parts[0]
        namespaces = parts[1:]

        package = requirement.Requirement(package)
        output[package].update(namespaces)

    return list(output.items())


def _make_absolute(path):
    """Convert `path` into an absolute file path.

    If `path` is a relative path, resolve it using the current working directory.

    Args:
        path (str): Some absolute or relative file / folder path to convert.

    Returns:
        str: An absolute file / folder path.

    """
    if os.path.isabs(path):
        return path

    current = os.getcwd()

    return os.path.normcase(os.path.join(current, path))


def _clean(item):
    """Remove any leading or trailing ""s from `item`."""
    return shlex.split(item)[0]


def _clean_items(text):
    """Remove any leading or trailing ""s from `text`."""
    return [_clean(item) for item in text]


def main(text):
    """Run the main execution of the current script.

    Args:
        text (list[str]): The raw CLI input, split by spaces.

    Raises:
        ValueError:
            If the user provides a directory to find a Rez package but
            the directory doesn't exist or there isn't a Rez package in
            the directory.

    """
    arguments = _parse_arguments(text)
    requirements = _expand(_clean_items(arguments.requirements))
    deprecate = _expand(_clean_items(arguments.deprecate))
    package_directory = _make_absolute(_clean(arguments.package_directory))
    package = inspection.get_nearest_rez_package(package_directory)

    if not package:
        raise ValueError(
            'Directory "{package_directory}" does not define a Rez package.'
            "".format(package_directory=package_directory)
        )

    # We have to split `arguments.command` twice. Once to get rid of the
    # surrounding ""s and the second time to actually split the tokens
    # into pieces.
    #
    command = shlex.split(arguments.command)[0]
    command_configuration = cli.parse_arguments(shlex.split(command))
    replacer.replace(package, command_configuration, requirements, deprecate)
