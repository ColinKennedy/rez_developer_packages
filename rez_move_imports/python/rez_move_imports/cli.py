#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The main module that parses the user's CLI input so ``rez_move_imports`` can work."""

import argparse
import collections
import os
import shlex

from move_break import cli
from rez.vendor.version import requirement
from rez_utilities import finder

from .core import exception, replacer


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
        "-n",
        "--no-bump",
        action="store_true",
        help="If added, don't bump the minor version of the Rez package, even if it was modified.",
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

        if not namespaces:
            raise exception.InvalidInput(
                'Text "{package_and_namespaces}" '
                "must be a list of Rez package + at least one Python namespace."
                "".format(package_and_namespaces=package_and_namespaces)
            )

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

    return os.path.normpath(os.path.join(current, path))


def _clean(item):
    """Remove any leading or trailing ""s from `item`."""
    return shlex.split(item)[0]


def _clean_items(text):
    """Remove any leading or trailing ""s from `text`."""
    return [_clean(item) for item in text]


def _check_namespaces(namespaces, deprecate, requirements):
    """Make sure that every Python namespace is linked to a Rez package.

    Args:
        namespaces (list[tuple[str, str]]):
            Python dot-separated namespaces that need to be changed.
            Each tuple is the existing namespace and the namespace that
            should replace it.
        deprecate (iter[tuple[str]]):
            The Python import namespaces of a Rez package that we are trying to remove.
        requirements (iter[tuple[str]]):
            The Python import namespaces of a Rez package that we are trying to add.

    Raises:
        :class:`.MissingNamespaces`:
            If any Python dot-separated import in `namespaces` was missing
            in `deprecate` or `requirements`.

    """

    def _is_included(namespace, namespaces):
        for package_namespaces in namespaces:
            if replacer.is_matching_namespace(namespace, package_namespaces):
                return True

        return False

    missing_olds = set()
    missing_news = set()

    for old_namespace, new_namespace in namespaces:
        if not _is_included(old_namespace, deprecate):
            missing_olds.add(old_namespace)

        if not _is_included(new_namespace, requirements):
            missing_news.add(new_namespace)

    if missing_olds:
        raise exception.MissingNamespaces(
            'Python namespaces "{namespaces}" are defined but not linked to a Rez package. '
            "Please add them to --deprecate".format(namespaces=sorted(missing_olds))
        )

    if missing_news:
        raise exception.MissingNamespaces(
            'Python namespaces "{namespaces}" are defined but not linked to a Rez package. '
            "Please add them to --requirements".format(namespaces=sorted(missing_news))
        )


def get_user_namespaces(text):
    """set[tuple[str, str]]: The old Python dot-separated namespace to replace + the new one."""
    arguments = _parse_arguments(text)
    command = arguments.command.strip('"').strip("'")
    command_configuration = cli.parse_arguments(shlex.split(command))

    return command_configuration.namespaces


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

    if not os.path.isdir(package_directory):
        raise exception.MissingDirectory(
            'Directory "{package_directory}" does not exist.'
            "".format(package_directory=package_directory)
        )

    package = finder.get_nearest_rez_package(package_directory)

    if not package:
        raise exception.InvalidDirectory(
            'Directory "{package_directory}" does not define a Rez package.'
            "".format(package_directory=package_directory)
        )

    # We have to split `arguments.command` twice. Once to get rid of the
    # surrounding ""s and the second time to actually split the tokens
    # into pieces.
    #
    command = arguments.command.strip('"').strip("'")
    command_configuration = cli.parse_arguments(shlex.split(command))

    _check_namespaces(
        command_configuration.namespaces,
        [namespaces for _, namespaces in deprecate],
        [namespaces for _, namespaces in requirements],
    )

    replacer.replace(
        package,
        command_configuration,
        deprecate,
        requirements,
        bump=not arguments.no_bump,
    )
