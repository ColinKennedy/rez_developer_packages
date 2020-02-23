#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The main module that reports / runs some plugin command.

"__main__.py" basically wraps this module with command-line-specific
details. This module does the actual work.

"""

import collections
import logging
import os
import shutil
import sys
import tempfile

import git
from rez import packages_
from rez_utilities import inspection, rez_configuration
from rezplugins.package_repository import filesystem

from . import exceptions, registry, rez_git
from .gitter import git_link

Skip = collections.namedtuple("Skip", "package path reason")
_LOGGER = logging.getLogger(__name__)


def _find_package_definitions(directory, name):
    """Find every Rez package matching some name in a folder on-disk.

    Args:
        directory (str): An absolute path to a folder that has Rez packages in it.
        name (str): The name of the Rez package to search for.

    Returns:
        set[:class:`rez.packages_.DeveloperPackage`]:
            The found packages. Usually, this will only ever have
            one package if found or empty, if not found. But if any
            duplicate packages are found, those will get returned, too.

    """
    matches = set()

    for root, _, files in os.walk(directory):
        for name_ in files:
            if name_ in rez_configuration.REZ_PACKAGE_NAMES:
                package = packages_.get_developer_package(root)

                if package.name == name:
                    matches.add(package)

    return matches


def handle_generic_exception(error, package):
    """Get a printable strin for an error get the path to the Rez package that triggered it.

    This function is mainly used for handling exceptions.

    Args:
        error (:class:`Exception`):
            Some Python exception.
        package (:class:`rez.packages_.DeveloperPackage`):
            The package that triggered the error.

    Returns:
        tuple[str, str]: The found path and the exception message.

    """
    # Plugin functions can raise any exception so they must be caught, here
    path = inspection.get_package_root(package)

    if hasattr(error, "message"):
        message = error.message
    else:
        message = str(error)

    if not message:
        try:
            message = error.value.short_msg
        except AttributeError:
            pass

    return path, str(message)


def report(
    packages_to_report,
    maximum_repositories=sys.maxint,
    maximum_rez_packages=sys.maxint,
):
    """Check Rez packages for missing documentation and return them all.

    Args:
        packages_to_report (iter[:class:`rez.packages_.Package`]):
            The Rez packages to check for a command.
        maximum_repositories (int, optional):
            The number of unique repositories to check for packages.
            If the queried packages live in more repositories than
            this given parameter, then this function will exit early.
            Default: :attr:`sys.maxint`.
        maximum_rez_packages (int, optional):
            The number of unique Rez packages to potentially report.
            If the queried packages live in more repositories than
            this given parameter, then this function will exit early.
            Default: :attr:`sys.maxint`.

    Returns:
        tuple[
            list[:class:`rez.packages_.Package`],
            list[:class:`.InvalidPackage`],
        ]:
            Every package that needs to have a command run on them
            followed by Rez packages that couldn't be checked if they
            need the command because something is wrong with the
            package.

    """
    repositories = []
    packages = []
    invalids = []

    for package in packages_to_report:
        if len(repositories) > maximum_repositories:
            break
        elif len(packages) > maximum_rez_packages:
            break

        try:
            repository = rez_git.get_repository_url(package)
        except (exceptions.InvalidPackage, exceptions.NoRepositoryRemote) as error:
            invalids.append(
                exceptions.InvalidPackage(
                    package, inspection.get_package_root(package), str(error)
                )
            )

            continue
        except filesystem.PackageDefinitionFileMissing as error:
            _LOGGER.exception(
                'A damaged Rez package "%s" was found. Please fix or remove it.',
                package,
                exc_info=True,
            )
            invalids.append(
                exceptions.InvalidPackage(
                    package, inspection.get_package_root(package), str(error)
                )
            )

            continue

        repositories.append(repository)
        packages.append(package)

    return packages, invalids


def run(  # pylint: disable=too-many-arguments,too-many-locals
    runner,
    packages_to_run,
    maximum_repositories=sys.maxint,
    maximum_rez_packages=sys.maxint,
    keep_temporary_files=False,
    temporary_directory="",
):
    """Run a command on the given Rez packages.

    Args:
        packages_to_run (iter[:class:`rez.packages_.Package`]):
            The Rez packages to run a command on. e.g. adding documentation.
        maximum_repositories (int, optional):
            The number of unique repositories to check for packages.
            If the queried packages live in more repositories than
            this given parameter, then this function will exit early.
            Default: :attr:`sys.maxint`.
        maximum_rez_packages (int, optional):
            The number of unique Rez packages to run the command onto.
            If the queried packages live in more repositories than
            this given parameter, then this function will exit early.
            Default: :attr:`sys.maxint`.
        keep_temporary_files (bool, optional):
            If False, delete any folders used to clone local git
            If repositories. True, don't delete them. Default is False.
        temporary_directory (str, optional):
            The folder where git repositories will be cloned to. If no
            folder is given, each repository is cloned to a separate
            temporary directory. Default: "".

    Returns:
        tuple[
            set[:class:`rez.packages_.Package`],
            set[tuple[:class:`rez.packages_.Package`, :class:`.CoreException`]],
            list[:class:`.InvalidPackage`],
        ]:
            Every Rez package that was successfully "ran" by the
            command, every Rez package did not get run for some reason,
            and every Rez package that had some kind of issue with the
            package so no command could be run.

    """

    def _group_by_repository(packages):
        output = collections.defaultdict(set)

        for package in packages:
            output[rez_git.get_repository_url(package)].add(package)

        return output.items()

    filtered_packages, invalids = report(
        packages_to_run,
        maximum_repositories=maximum_repositories,
        maximum_rez_packages=maximum_rez_packages,
    )

    ran = set()
    un_ran = set()

    for repository_url, packages in _group_by_repository(filtered_packages):
        # TODO : Add thing to make this more quiet, if needed
        if not temporary_directory:
            clone_directory = tempfile.mkdtemp(
                suffix="_{name}_pull_request_location".format(
                    name=repository_url.split("/")[-1]
                )
            )
            # `git.Repo.clone_from` requires that the directory not already exist.
            # But we need the temporary directory name. So remove the directory
            #
            shutil.rmtree(clone_directory)
        else:
            clone_directory = git_link.make_repository_folder(
                temporary_directory, repository_url
            )

        if not os.path.isdir(clone_directory):
            os.makedirs(clone_directory)
            repository = git.Repo.clone_from(repository_url, clone_directory)
        else:
            repository = git.Repo(clone_directory)

        repository_root = repository.working_dir

        if not keep_temporary_files:
            git_link.add_directory_to_delete(repository_root)

        for package in packages:
            definitions = list(_find_package_definitions(repository_root, package.name))

            if not definitions:
                un_ran.add(
                    package,
                    'Could not find "{package.name}" in repository "{repository_root}".'
                    "".format(package=package, repository_root=repository_root),
                )

                continue
            elif len(definitions) > 1:
                # TODO : Finish the report logic for this one
                un_ran.add(
                    list(definitions),
                    'More than one package definition "{package.name}" was found '
                    'in repository "{repository_root}".'
                    "".format(package=package, repository_root=repository_root),
                )

                continue

            inner_repository_package = definitions[0]

            try:
                error = runner(inner_repository_package)
            except exceptions.CoreException as error:  # pylint: disable=broad-except
                un_ran.add((inner_repository_package, error))

                continue

            if error:
                un_ran.add((inner_repository_package, error))
            else:
                ran.add(inner_repository_package)

    return ran, un_ran, invalids
