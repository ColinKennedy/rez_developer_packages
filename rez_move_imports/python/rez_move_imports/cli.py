#!/usr/bin/env python
# -*- coding: utf-8 -*-


import argparse
import shlex

from move_break import cli


def _parse_arguments(text):
    parser = argparse.ArgumentParser(
        description="Change a Rez package's imports and then bump the require Rez version(s).",
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

    return parser.parse_args(text)


def _split_package_and_namespaces(package_and_namespaces):
    parts = []

    for item in package_and_namespaces.split(","):
        item = item.strip()

        if item:
            parts.append(item)

    return parts


def _expand(items):
    output = dict()

    for package_and_namespaces in items:
        parts = _split_package_and_namespaces(package_and_namespaces)
        package = parts[0]
        namespaces = parts[1:]

        output[package] = namespaces

    return output


def main(text):
    # """Run the main execution of the current script."""
    arguments = _parse_arguments(text)
    requirements = _expand(arguments.requirements)
    deprecate = _expand(arguments.deprecate)

    cli.main(shlex.split(arguments.command))
