#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import atexit
import functools
import logging
import os
import shutil
import sys
import tempfile
import textwrap

import git
from rez import exceptions as rez_exceptions
from rez import packages_, serialise
from rez_batch_process import cli
from rez_batch_process.core import exceptions, registry, worker
from rez_batch_process.core.plugins import command, conditional
from rez_utilities import inspection
from rez_utilities_git import gitter
from six.moves import io

_LOGGER = logging.getLogger(__name__)


class Yaml2Py(command.RezShellCommand):
    @staticmethod
    def _get_pull_request_body(package, _):
        """str: Convert a Rez package into a description for pull requests from this class."""
        # TODO : Change URL to the master branch (or a commit) just before merging
        template = textwrap.dedent(
            """\
            This PR converts the package.yaml of ``{package.name}`` into a package.py file.

            ## Why

            package.yaml files don't support many Rez features, like:

            - [@early()](https://github.com/nerdvegas/rez/wiki/Package-Definition-Guide#early-binding-functions)
            - [@late()](https://github.com/nerdvegas/rez/wiki/Package-Definition-Guide#late-binding-functions)
            - rez-tests
            - execution logic in commands()

            and much more.

            It's also pretty easy to convert package.yaml to package.py
            so there's basically no reason not to.

            ## How

            This PR was generated automatically, using
            [``rez_batch_plugins``](https://github.com/ColinKennedy/rez_developer_packages/tree/add_rez_batch_plugins/rez_batch_plugins)

            ## Who this PR is for

            Anyone that maintains ``{package.name}``

            ## What should you do

            **Approve the PR :)**
            """
        )

        return template.format(package=package)

    @staticmethod
    def _run_command(package, arguments):
        # """Run the user-provided command on the given Rez package.
        #
        # Args:
        #     package (:class:`rez.developer_package.DeveloperPackage`):
        #         The Rez package that will be used changed. Any command
        #         run by this function will do so while cd'ed into the
        #         directory of this package.
        #     arguments (:class:`argparse.Namespace`):
        #         The user-provided, plug-in specific arguments.
        #         Specifically, this should bring in
        #
        #         - The command that the user wants to run, per-package
        #         - The name of the ticket that will be used for git branches
        #         - The option to "raise an exception if any error occurs"
        #           or whether it's OK to continue.
        #
        # Raises:
        #     :class:`.CoreException`:
        #         If ``exit_on_error`` is enabled and the user-provided
        #         command fails, for any reason.
        #
        # Returns:
        #     str: Any error message that occurred from this command, if any.
        #
        # """
        if not package.filepath.endswith(".yaml"):
            raise exceptions.InvalidPackage(
                package,
                inspection.get_package_root(package),
                'Package "{package}" is not a YAML file.'.format(package=package),
            )

        buffer_ = io.StringIO()
        package.print_info(format_=serialise.FileFormat.py, buf=buffer_)
        code = buffer_.getvalue()

        path = os.path.join(inspection.get_package_root(package), "package.py")
        _LOGGER.info('Now creating "%s".', path)

        with open(path, "w") as handler:
            handler.write(code)

        _LOGGER.info('Now removing the old "%s".', package.filepath)

        os.remove(package.filepath)

        return ""

    @staticmethod
    def parse_arguments(text):
        parser = argparse.ArgumentParser(
            description="Run rez-yaml2py on all package.yaml files."
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

        _LOGGER.info('Pull request posted for "%s".', package.name)

        return ""


def _is_keep_temporary_files_enabled():
    arguments, _ = cli.parse_arguments(sys.argv[1:])

    return arguments.keep_temporary_files


def _is_python_definition(package):
    if not inspection.is_built_package(package):
        path = inspection.get_package_root(package)

        try:
            packages_.get_developer_package(path, format=serialise.FileFormat.py)
        except rez_exceptions.PackageMetadataError:
            return False

        return True

    repository = _get_repository(package)
    repository_package = _get_package(repository.working_dir, package.name)

    return _is_python_definition(repository_package)


def _get_package(directory, name):
    for package in inspection.get_all_packages(directory):
        if package.name == name:
            return package

    return None


def _get_non_python_packages(paths=None):
    output = []

    packages, invalids, skips = conditional.get_default_latest_packages(paths=paths)

    for package in packages:
        if not package.name == "some_package":
            # TODO : Remove this part later
            continue

        if _is_python_definition(package):
            skips.append(
                worker.Skip(
                    package,
                    inspection.get_package_root(package),
                    "already has a package.py file.",
                )
            )

            continue

        output.append(package)

    return output, invalids, skips


def _get_repository_name(uri):
    base = uri.split("/")[-1]

    if base.endswith(".git"):
        base = base[: -1 * len(".git")]

    return base


def _get_repository(package):
    directory = _get_temporary_directory()
    uri = gitter.get_repository_url(package)
    name = _get_repository_name(uri)
    destination = os.path.join(directory, name)

    if os.path.isdir(destination):
        repository = git.Repo(destination)
    else:
        repository = git.Repo.clone_from(uri, destination)

    if not _is_keep_temporary_files_enabled():
        atexit.register(functools.partial(shutil.rmtree, repository.working_dir))

    return repository


def _get_temporary_directory():
    arguments, _ = cli.parse_arguments(sys.argv[1:])

    return arguments.temporary_directory or tempfile.mkdtemp(
        suffix="_some_location_to_clone_repositories"
    )


def main():
    """Run the main execution of the current script."""
    registry.register_plugin("yaml2py", _get_non_python_packages)
    registry.register_command("yaml2py", Yaml2Py)
