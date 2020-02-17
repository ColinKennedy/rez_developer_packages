#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse

from rez_batch_process.core.plugins import command


class RezShellCommand(command.RezShellCommand):
    @staticmethod
    def _get_pull_request_body(package):
        """str: Convert a Rez package into a description for pull requests from this class."""
        template = textwrap.dedent(
            """\
            This PR converts package.yaml files into package.py files.

            ## Why

            package.yaml files don't support many Rez features, like:

            - [@early()](https://github.com/nerdvegas/rez/wiki/Package-Definition-Guide#early-binding-functions)
            - [@late()](https://github.com/nerdvegas/rez/wiki/Package-Definition-Guide#late-binding-functions)
            - rez-tests
            - execution logic in commands()

            and much more.

            Also, all Rez package examples online, including every style guide
            use package.py as a standard.

            ## How

            This PR was generated automatically, using [rez_batch_plugins]()

            Hello, World!

            This PR was created automatically.

            ## Who this PR is for

            Anyone that maintains ``{package.name}``

            ## What should you do

            **Approve the PR :)**
            """
        )

        return template.format(package=package)
    @staticmethod
    def parse_arguments(text):
        parser = argparse.ArgumentParser(
            description="Run rez-yaml2py on all package.yaml files.",
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
            "-e",
            "--exit-on-error",
            action="store_true",
            help="If running rez-yaml2py on a package raises an exception "
            "and this flag is added, this command will bail out early.",
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

    @classmethod
    def run(cls, package, arguments):
        error = cls._run_command(package, arguments)

        if error:
            return error

        cls._create_pull_request(
            package,
            command.Configuration(
                "rez-yaml2py",
                arguments.token,
                arguments.pull_request_prefix,
                arguments.ssl_no_verify,
            ),
            cached_users=arguments.cached_users,
            fallback_reviewers=arguments.fallback_reviewers,
            base_url=arguments.base_url,
        )

        return ""

