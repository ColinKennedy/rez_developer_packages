#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""A tool which specializes in bumping Rez package dependencies."""

import textwrap
import argparse

from rez_batch_process.core.plugins import command


class Bump(command.RezShellCommand):
    """A class that forces downstream Rez packages to accept a new Rez package version."""

    @staticmethod
    def _get_pull_request_body(package, configuration):
        """str: Convert a Rez package into a description for pull requests from this class."""
        template = textwrap.dedent(
            """\
            This PR bumps a Rez package because one-or-more of its
            dependencies have changed.

            Normally, you'd only need to do this when a dependency
            releases a new major version. Which means that the
            dependency's API must have changed in a way that could break
            your code.

            ## Extra Instructions
            {configuration.instructions}

            ## Testing
            ### Pre-Bump
            Does it build? {configuration.pre_bump_build}
            Does testing pass? {configuration.pre_bump_test}

            ### Post-Bump
            Does it build? **{configuration.post_bump_build}**
            Does testing pass? **{configuration.post_bump_test}**

            ## Reviewer Expectations
            Please review this PR to ensure

            A. That the code changes look correct
            B. The affected packages build
            C. rez-test still works for said package(s)

            Once that's done, this PR should be good to merge.

            Thanks for your review!
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
            description="Find downstream packages affected by a new package's version."
        )
        raise NotImplementedError('Need to make sure --packages creates a list')
        parser.add_argument(
            "--packages",
            required=True,
            help="The name of the package/version that will be bumped in all downstream packages.",
        )
        parser.add_argument(
            "-i",
            "--instrunctions",
            required=True,
            help="Explain any other special notes that you want PR reviewers to know.",
        )
        parser.add_argument(
            "-s",
            "--search-paths",
            help="An optional set of paths to include "
        )

        command.add_git_arguments(parser)

        return parser.parse_args(text)

    @classmethod
    def _run_command(cls, package, arguments):
        """Run the main bump command on a Rez package.

        Args:
            package (:class:`rez.developer_package.DeveloperPackage`):
                The Rez package that will be changed. Any command
                run by this function will do so while cd'ed into the
                directory of this package.

                To be clear, this Rez package represents one of the downstream packages
                whose version + dependenc(ies) will be changed.
            arguments (:class:`argparse.Namespace`):
                The user-provided, plug-in specific arguments.
                Specifically, this should bring in

                - The command that the user wants to run, per-package
                - The name of the ticket that will be used for git branches
                - The option to "raise an exception if any error occurs"
                  or whether it's OK to continue.

        Returns:
            str: Any error message that occurred from this command, if any.

        """
        raise NotImplementedError('asdfasd')

        return super(Bump, cls)._run_command(package, arguments)

    @classmethod
    def run(cls, package, arguments):
        """Run a command on a package and create a pull request.

        Args:
            package (:class:`rez.developer_package.DeveloperPackage`):
                The Rez package that will be used changed. Any command
                run by this function will do so while cd'ed into the
                directory of this package.
            arguments (:class:`argparse.Namespace`):
                The user-provided, plug-in specific arguments.
                Specifically, this should bring in

                - The command that the user wants to run, per-package
                - The name of the ticket that will be used for git branches
                - The option to "raise an exception if any error occurs"
                  or whether it's OK to continue.

        Returns:
            str: Any error message that occurred from this command, if any.

        """
        cls._run_command(package, arguments)

        cls._create_pull_request(
            package,
            command.Configuration(
                "bump",
                arguments.token,
                arguments.pull_request_name,
                arguments.ssl_no_verify,
            ),
            cached_users=arguments.cached_users,
            fallback_reviewers=arguments.fallback_reviewers,
            base_url=arguments.base_url,
        )

        return ""
