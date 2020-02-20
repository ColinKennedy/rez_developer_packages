#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The module that contains extensible commands for modifying Rez packages."""

import argparse
import collections
import logging
import subprocess
import textwrap

from rez_utilities import inspection

from .. import exceptions, rez_git
from ..gitter import base_adapter, git_link, git_registry
from . import base

_LOGGER = logging.getLogger(__name__)
Configuration = collections.namedtuple(
    "Configuration", "command token pull_request_prefix ssl_no_verify"
)


# TODO : Add unittest to make sure this plugin thing works
class RezShellCommand(base.BaseCommand):
    """The main class runs 1 command once per-Rez-package to create a pull request.

    On its own, this class does nothing. It requires the user to provide
    a shell command which it will then execute, once per-Rez-package,
    and make a new PR per change.

    """

    @staticmethod
    def _get_commit_message(package):
        """Create text git will use for any git commit messages caused by this command.

        Args:
            package (str): The name of the Rez package that was modified.

        Returns:
            str: The generated message.

        """
        return 'Updated "{package}".'.format(package=package)

    @staticmethod
    def _get_pull_request_body(package, _):
        """str: Convert a Rez package into a description for pull requests from this class."""
        template = textwrap.dedent(
            """\
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
    def _run_command(package, arguments):
        """Run the user-provided command on the given Rez package.

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

        Raises:
            :class:`.CoreException`:
                If ``exit_on_error`` is enabled and the user-provided
                command fails, for any reason.

        Returns:
            str: Any error message that occurred from this command, if any.

        """
        command = 'cd "{root}";{arguments.command}'.format(
            root=inspection.get_package_root(package), arguments=arguments
        )
        _LOGGER.debug('Command to run "%s".', command)

        process = subprocess.Popen(
            command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        stdout, stderr = process.communicate()
        _LOGGER.debug('stdout "%s".', stdout)

        if stderr:
            message = (
                'Package "{package.name}" raised an error when '
                '"{command}" command was run. The command may '
                "not have been added correctly.".format(
                    package=package, command=command
                )
            )

            if arguments.exit_on_error:
                raise exceptions.CoreException(message)

            return message

        return ""

    @classmethod
    def _create_pull_request(  # pylint: disable=too-many-arguments,too-many-locals
        cls,
        package,
        configuration,
        cached_users="",
        fallback_reviewers=None,
        base_url="",
    ):
        """Make a pull request for whatever changes were done to a Rez package.

        Args:
            package (:class:`rez.packages_.Package`):
                The object that should either have a git repository defined
                or is itself inside of a git repository.
            configuration (:attr:`Configuration`):
                A set of options for creating the pull request. It
                contains the shell command that will be run on the Rez
                package, the authentication string that is used to
                connect to GitHub / bitbucket, and a string prefix to
                use for creating the pull requests.
            cached_users (str, optional):
                The path to the cached remote users, if one exists.
                Basically, querying users in sites like GitHub
                takes a ton of time, which causes re-running
                ``rez_batch_process`` to be very slow. This
                parameter lets you cache the so user data doesn't need
                to be queried over and over.
            fallback_reviewers (list[str]):
                The usernames of people who will be assigned to pull
                requests if there are not enough people to review the change.
            base_url (str, optional):
                The API url that is used if the user needs to access
                a non-standard remote location. For example, if the
                user is working in GitHub Enterprise and not regular
                GitHub, they'll need to provide a `base_url` to the
                GitHub Enterprise URL to authenticate. Default: "".

        Raises:
            NotImplementedError:
                If the package's repository's git URL is hosted by
                something that this tool doesn't know how to process.

        """
        if not fallback_reviewers:
            fallback_reviewers = []

        repository = rez_git.get_repository(package)
        current_branch = repository.active_branch
        repository.head.reset(  # Make sure there are no uncommitted changes
            index=True, working_tree=True
        )

        origin = repository.remote(name="origin")
        origin.pull(current_branch)

        url = rez_git.get_repository_url_from_repository(repository)
        adapter = git_registry.get_remote_adapter(
            package,
            url,
            configuration.token,
            fallback_reviewers=fallback_reviewers,
            base_url=base_url,
            verify=configuration.ssl_no_verify,
        )

        if not adapter:
            raise NotImplementedError(
                'No adapter could be found for git repository "{url}".'.format(url=url)
            )

        title = 'Ran command "{configuration.command}" on Rez package "{package.name}".'.format(
            configuration=configuration, package=package
        )
        # TODO : Change this spot to actually use the repository's default branch
        body = cls._get_pull_request_body(package, configuration)
        commit_message = cls._get_commit_message(package.name)

        branch_template = (
            "{configuration.pull_request_prefix}_{package.name}_run_command"
            "".format(configuration=configuration, package=package)
        )
        new_branch_name = _get_unique_branch(repository, branch_template)
        new_branch = repository.create_head(new_branch_name)
        new_branch.checkout()

        try:
            git_link.add_everything_in_repository(repository)
            repository.index.commit(commit_message)
            origin = repository.remote(name="origin")
            origin.push(
                refspec="{new_branch.name}:{new_branch.name}".format(
                    new_branch=new_branch
                )
            )

            adapter.create_pull_request(
                title,
                body,
                base_adapter.PullRequestDetails(
                    url,
                    new_branch.name,
                    current_branch.name,
                ),
                user_data=cached_users,
                verify=configuration.ssl_no_verify,
            )
        except Exception:  # pylint: disable=broad-except
            _LOGGER.exception("No pull request could be created")

            raise
        finally:
            # Revert back to the previous branch
            current_branch.checkout()

    @staticmethod
    def parse_arguments(text):
        """Make sure the user's input has everything this class needs in order to run.

        This method is your opportunity to request extra information
        from the user before running your command. This parser is meant
        to operate on whatever the main CLI parser doesn't pick up.

        Important:
            This main CLI parser checks for all known arguments. The
            rest of the arguments that could not get parsed are passed
            to this class. That means that this method should aim to
            capture 100% of its input. Because the input should always
            be "plug-in specific" arguments.

        Args:
            text (list[str]):
                The user-provided arguments that this function must process.

        Returns:
            :class:`argparse.Namespace`: The found, plug-in specific arguments.

        """
        parser = argparse.ArgumentParser(
            description="Run some command on Rez packages."
        )
        parser.add_argument(
            "command",
            help="The shell command that will be run while cd'ed into every Rez package.",
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
            help="If running the command on a package raises an exception "
            "and this flag is added, this class will bail out early.",
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
        """Run a shell command on a given Rez package, based on the user's input.

        Args:
            package (:class:`rez.packages_.Package`):
                Some Rez package to process.
            arguments (:class:`argparse.Namespace`):
                The plug-in specific arguments that were given by the
                user to help this function do its work.

        Returns:
            str: If any error was found while the function was executed.

        """
        error = cls._run_command(package, arguments)

        if error:
            return error

        cls._create_pull_request(
            package,
            Configuration(
                arguments.command,
                arguments.token,
                arguments.pull_request_prefix,
                arguments.ssl_no_verify,
            ),
            cached_users=arguments.cached_users,
            fallback_reviewers=arguments.fallback_reviewers,
            base_url=arguments.base_url,
        )

        return ""


def _get_unique_branch(repository, base_branch_name):
    """Get a git branch name that has not been used before by a repository.

    Args:
        repository (:class:`git.Repo`):
            The Git repository that will be used to query existing branch names.
        base_branch_name (str):
            A suggested branch name that will be used to find a unique
            name. If `base_branch_name` is not a current branch in `repository` then
            `base_branch_name` will be returned by this function.

    Returns:
        str: The found unique branch name.

    """

    def _has_branch(repository, branch):
        for existing in repository.branches:
            if existing.name == branch:
                return True

        return False

    branch = base_branch_name
    index = 1

    while _has_branch(repository, branch):
        branch = base_branch_name + "_{index}".format(index=index)
        index += 1

    return branch
