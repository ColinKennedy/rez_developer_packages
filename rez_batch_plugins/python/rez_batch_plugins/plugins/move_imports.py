#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""A class that automatically refactors moved Python modules."""

import argparse
import textwrap

from rez_batch_process.core import registry
from rez_batch_process.core.plugins import command, conditional


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

        super(MoveImports, cls)._run_command(package, arguments)

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


def main():
    """Add :class:`.MoveImports` to ``rez_batch_process``."""
    registry.register_plugin("move_imports", conditional.get_default_latest_packages)
    registry.register_command("move_imports", MoveImports)
