#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""A class that automatically refactors moved Python modules."""

import argparse
import shlex
import sys
import textwrap

from rez import serialise
from python_compatibility import dependency_analyzer
from rez_batch_process import cli as rez_batch_process_cli
from rez_batch_process.core import registry, worker
from rez_batch_process.core.plugins import command, conditional
from move_break import move_break_api
from rez_move_imports import cli as rez_move_imports_cli
from rez_utilities import inspection

from .. import repository_area


class MoveImports(command.RezShellCommand):
    """A class that automatically refactors moved Python modules."""

    @staticmethod
    def _get_pull_request_body(package, configuration):
        """str: Convert a Rez package into a description for pull requests from this class."""
        template = textwrap.dedent(
            """\
            This PR moves Python imports from one location to another
            and auto-adds Rez dependencies for those imports to Rez
            packages that need them.

            If you're seeing this, chances are, modules from a popular
            Rez package were moved to a new location and we're just
            trying to update the imports + dependencies to keep
            everything up to date.

            ## Why

            {configuration.why}

            ## How

            This PR was generated automatically, using
            [``rez_batch_plugins``](https://github.com/ColinKennedy/rez_developer_packages/tree/add_rez_batch_plugins/rez_batch_plugins)

            Specially, using the [``move_imports``](https://github.com/ColinKennedy/rez_developer_packages/tree/add_rez_batch_plugins/rez_batch_plugins)
            plugin.

            ## Who this PR is for

            Anyone that maintains ``{package.name}``

            ## What should you do

            Please check the PR to make sure the generated output is
            valid. Hopefully everything went okay and you just need to
            approve the PR. But if there's tests unexpectedly failing or
            there's extra steps needed to make the new code work, please
            help this script by making these changes yourself and then
            approve the PR.
            """
        )

        return template.format(package=package, configuration=configuration)

    @staticmethod
    def parse_arguments(text):
        """Parse user-provided CLI text into inputs that this class understands.

        Args:
            text (list[str]): The user provided input, separated by spaces.

        Returns:
            :class:`argparse.Namespace`: The parsed output.

        """
        parser = argparse.ArgumentParser(
            description="Replace Python imports for Rez packages."
        )
        parser.add_argument(
            "-w",
            "--why",
            required=True,
            help="Explain what imports you're changing and why you're changing them.",
        )
        parser.add_argument(
            "-a",
            "--arguments",
            required=True,
            help="The code that'll be sent directly to rez_move_imports",
        )
        parser.add_argument(
            "-e",
            "--exit-on-error",
            action="store_true",
            help="If running the command on a package raises an exception "
            "and this flag is added, this class will bail out early.",
        )

        command.add_git_arguments(parser)

        return parser.parse_args(text)

    @classmethod
    def _run_command(cls, package, arguments):
        arguments.command = "python -m rez_move_imports " + arguments.arguments

        return super(MoveImports, cls)._run_command(package, arguments)

    @classmethod
    def run(cls, package, arguments):
        cls._run_command(package, arguments)

        cls._create_pull_request(
            package,
            command.Configuration(
                "move_imports",
                arguments.token,
                arguments.pull_request_name,
                arguments.ssl_no_verify,
            ),
            cached_users=arguments.cached_users,
            fallback_reviewers=arguments.fallback_reviewers,
            base_url=arguments.base_url,
        )

        return ""


def _needs_replacement(package, user_namespaces):
    """Figure out if the Rez package has Python files in it that :class:`MoveImports` can act upon.

    The logic goes like this:

    - A Rez source python package is assumed to have all its files available
        - Return whether namespaces are found
    - If the Rez python package is a released package though, we can't just assume all Python files are available.
        - The built Rez package may output an .egg or .whl file, for example
        - So if namespaces are found, then return True
        - If no namespaces are found, clone the package's repository and try again

    Args:
        package (:class:`rez.packages_.Package`):
            Some Rez package (source or released package) to check for Python imports.

    Returns:
        bool:
            If any of the user-provided Python namespaces were found
            inside of the given `package`.

    """
    root = inspection.get_package_root(package)
    package = inspection.get_nearest_rez_package(root)

    namespaces = set()

    for path in move_break_api.expand_paths(root):
        if path == package.filepath:
            continue

        namespaces.update(move_break_api.get_namespaces(path))

    if namespaces.intersection(user_namespaces):
        return True

    if not inspection.is_built_package(package):
        return False

    repository = repository_area.get_repository(package)
    repository_package = repository_area.get_package(repository.working_dir, package.name)

    return _needs_replacement(repository_package, user_namespaces)


def _get_user_provided_namespaces():
    _, arguments = rez_batch_process_cli.parse_arguments(sys.argv[1:])

    return rez_move_imports_cli.get_user_namespaces(shlex.split(arguments.arguments))


def _get_packages_which_must_be_changed(paths=None):
    packages, invalids, skips = conditional.get_default_latest_packages(paths=paths)
    user_provided_namespaces = _get_user_provided_namespaces()
    expected_existing_namespaces = {old for old, _ in user_provided_namespaces}
    output = []

    for package in packages:
        if not repository_area.is_python_definition(package, serialise.FileFormat.py):
            skips.append(
                worker.Skip(
                    package,
                    inspection.get_package_root(package),
                    "does not define a package.py file."
                )
            )

            continue

        if not _needs_replacement(package, expected_existing_namespaces):
            skips.append(
                worker.Skip(
                    package,
                    inspection.get_package_root(package),
                    "No namespaces need to be replaced.",
                )
            )

            continue

        output.append(package)

    return output, invalids, skips


def main():
    """Add :class:`.MoveImports` to ``rez_batch_process``."""
    registry.register_plugin("move_imports", _get_packages_which_must_be_changed)
    registry.register_command("move_imports", MoveImports)
