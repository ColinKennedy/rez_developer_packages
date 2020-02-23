#!/usr/bin/env python
# -*- coding: utf-8 -*-

# pylint: disable=line-too-long
"""A class that converts Rez package.yaml to package.py files."""

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
    """A class that converts Rez package.yaml to package.py files."""

    @staticmethod
    def _get_pull_request_body(package, _):
        """str: Convert a Rez package into a description for pull requests from this class."""
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
            [``rez_batch_plugins``](https://github.com/ColinKennedy/rez_developer_packages/tree/master/rez_batch_plugins)

            ## Who this PR is for

            Anyone that maintains ``{package.name}``

            ## What should you do

            **Approve the PR :)**
            """
        )

        return template.format(package=package)

    @staticmethod
    def _run_command_on_package(package):
        """Run the user-provided command on the given Rez package.

        Args:
            package (:class:`rez.developer_package.DeveloperPackage`):
                The Rez package that presumably is a package.yaml file
                that needs to be changed.

        Raises:
            :class:`.InvalidPackage:
                If `package` is not a package.yaml file.

        Returns:
            str: Any error message that occurred from this command, if any.

        """
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
        """Parse the user-provided text into something that this class understands.

        Args:
            text (list[str]): The space-separated flags that the user provided.

        Returns:
            :class:`argparse.Namespace`: The user-provided text, converted to Python objects.

        """
        parser = argparse.ArgumentParser(
            description="Run rez-yaml2py on all package.yaml files."
        )
        command.add_git_arguments(parser)

        return parser.parse_args(text)

    @classmethod
    def run(cls, package, arguments):
        """Run `rez-yaml2py` and then submit a pull request.

        Args:
            package (:class:`rez.packages_.Package`):
                Some Rez package to process.
            arguments (:class:`argparse.Namespace`):
                The plug-in specific arguments that were given by the
                user to help this function do its work.

        Returns:
            str: If any error was found while the function was executed.

        """
        error = cls._run_command_on_package(package)

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
    """bool: Check if the user asked to not delete auto-generated files."""
    arguments, _ = cli.parse_arguments(sys.argv[1:])

    return arguments.keep_temporary_files


def _is_yaml_definition(package):
    """Check if the given package defines a package.py file or something else.

    Args:
        package (:class:`rez.packages_.DeveloperPackage`):
            A package on-disk that will be verified.

    Returns:
        bool: If `package` defines a package.py, return True. Otherwise, return False.

    """
    if not inspection.is_built_package(package):
        path = inspection.get_package_root(package)

        try:
            packages_.get_developer_package(path, format=serialise.FileFormat.yaml)
        except rez_exceptions.PackageMetadataError:
            return False

        return True

    repository = _get_repository(package)
    repository_package = _get_package(repository.working_dir, package.name)

    return _is_yaml_definition(repository_package)


def _get_package(directory, name):
    """Find the Rez package within some directory matching the given name.

    Args:
        directory (str):
            The absolute path to some folder on-disk which contains Rez packages.
        name (str):
            A Rez package family that will be searched.

    Returns:
        :class:`rez.packages_.DeveloperPackage` or NoneType: The found package, if any.

    """
    for package in inspection.get_all_packages(directory):
        if package.name == name:
            return package

    return None


def _get_non_python_packages(paths=None):
    """Find every Rez package that defines a package.yaml file.

    Args:
        paths (list[str], optional):
            The directories used to search for Rez packages. If no paths
            are given, :attr:`rez.config.config.packages_path` will be
            used instead.

    Returns:
        tuple[:class:`rez.packages_.Package`, list, list]:
            All of the found Rez packages and a list of any Rez package
            that was considered invalid or any Rez packages that were
            valid but must be skipped, for some reason.

    """
    output = []

    packages, invalids, skips = conditional.get_default_latest_packages(paths=paths)

    for package in packages:
        if not _is_yaml_definition(package):
            skips.append(
                worker.Skip(
                    package,
                    inspection.get_package_root(package),
                    "is not a package.yaml file.",
                )
            )

            continue

        output.append(package)

    return output, invalids, skips


def _get_repository_name(uri):
    """str: Get the name that a Git repository will be called once it's cloned to-disk."""
    base = uri.split("/")[-1]

    if base.endswith(".git"):
        base = base[: -1 * len(".git")]

    return base


def _get_repository(package):
    """Clone the git repository of a Rez package to-disk and return it.

    Args:
        package (:class:`rez.packages_.DeveloperPackage`): A package to clone.

    Returns:
        :class:`git.Repo`: The cloned location that contained `package`.

    """
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
    """str: Get the directory used for cloning Rez repositories to-disk."""
    arguments, _ = cli.parse_arguments(sys.argv[1:])

    return arguments.temporary_directory or tempfile.mkdtemp(
        suffix="_some_location_to_clone_repositories"
    )


def main():
    """Run the main execution of the current script.

    This function will be called by ``rez_batch_process`` once the user
    calls it from command-line.

    """
    registry.register_plugin("yaml2py", _get_non_python_packages)
    registry.register_command("yaml2py", Yaml2Py)
