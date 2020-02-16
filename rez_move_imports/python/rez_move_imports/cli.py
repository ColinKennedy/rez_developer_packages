#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import collections
import os
import shlex

from move_break import cli
from rez import packages_
from rez_utilities import inspection

from .core import replacer


def _parse_arguments(text):
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
    parts = []

    for item in package_and_namespaces.split(","):
        item = item.strip()

        if item:
            parts.append(item)

    return parts


def _expand(items):
    output = collections.defaultdict(set)

    for package_and_namespaces in items:
        parts = _split_package_and_namespaces(package_and_namespaces)
        package = parts[0]
        namespaces = parts[1:]

        output[package].update(namespaces)

    return list(output.items())


def _make_absolute(path):
    if os.path.isabs(path):
        return path

    current = os.getcwd()

    return os.path.normcase(os.path.join(current, path))


def _clean(item):
    return shlex.split(item)[0]


def _clean_items(text):
    return [_clean(item) for item in text]


def main(text):
    # """Run the main execution of the current script."""
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
