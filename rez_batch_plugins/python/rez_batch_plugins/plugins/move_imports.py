#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import textwrap

from rez_batch_process.core.plugins import command


class RezShellCommand(command.RezShellCommand):
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
        parser = argparse.ArgumentParser(
            description="Replace Python imports for Rez packages.",
        )
        parser.add_argument(
            "pull_request_prefix",
            help="When new git branches are created, their names will start with this string.",
        )
        parser.add_argument(
            "token",
            help="The authentication token to the remote git repository (GitHub, bitbucket, etc).",
        )
        parser.add_argument(
            "-w",
            "--why",
            required=True,
            help="Explain what imports you're changing and why you're changing them.",
        )
        parser.add_argument(
            "-f",
            "--fallback-reviewers",
            nargs="+",
            default=[],
            help="If a git repository doesn't have many maintainers, "
            "this list of GitHub/Bitbucket users will review the PRs, instead.",
        )
        parser.add_argument(
            "-c",
            "--cached-users",
            help="A file that contains GitHub/bitbucket/etc usernames, "
            "emails, and login info. Must be a JSON file.",
        )
        parser.add_argument(
            "-b",
            "--base-url",
            help="If you are authenticating to a non-standard remote "
            "(e.g. GitHub enterprise), use this flag to provide the URL.",
        )
        parser.add_argument(
            "-s",
            "--ssl-no-verify",
            action="store_false",
            help="Disable SSL verification",
        )

        return parser.parse_args(text)

    @staticmethod
    def _run_command(package, arguments):
        raise NotImplementedError('Need to implement this')

    @classmethod
    def run(cls, package, arguments):
        cls._run_command(package, arguments)

        cls._create_pull_request(
            package,
            command.Configuration(
                "move_imports",
                arguments.token,
                arguments.pull_request_prefix,
                arguments.ssl_no_verify,
            ),
            cached_users=arguments.cached_users,
            fallback_reviewers=arguments.fallback_reviewers,
            base_url=arguments.base_url,
        )

        return ""
