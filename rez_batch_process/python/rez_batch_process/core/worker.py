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
from rez import exceptions as rez_exceptions
from rez import packages_
from rez_utilities import inspection, rez_configuration
from rezplugins.package_repository import filesystem

from . import exceptions, finder, registry, rez_git
from .gitter import git_link

Skip = collections.namedtuple("Skip", "package path reason")
_LOGGER = logging.getLogger(__name__)


# TODO : Add docstring
def _find_package_definitions(directory, name):
    matches = set()

    for root, _, files in os.walk(directory):
        for name_ in files:
            if name_ in rez_configuration.REZ_PACKAGE_NAMES:
                package = packages_.get_developer_package(root)

                if package.name == name:
                    matches.add(package)

    return matches


def handle_generic_exception(error, package):
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
    paths=None,
):
    """Check Rez packages for missing documentation and return them all.

    Args:
        packages_to_report (iter[:class:`rez.packages_.Package`]):
            The Rez packages to check for documentation.
        maximum_repositories (int, optional):
            The number of unique repositories to check for packages.
            If the queried packages live in more repositories than
            this given parameter, then this function will exit early.
            Default: :attr:`sys.maxint`.
        maximum_rez_packages (int, optional):
            The number of unique Rez packages to check for
            documentation. If the queried packages live in more
            repositories than this given parameter, then this function
            will exit early. Default: :attr:`sys.maxint`.
        paths (list[str], optional):
            The locations on-disk that will be used to any
            Rez-environment-related work. Some plugins need these
            paths for resolving a context, for example. Default is None.

    Returns:
        tuple[
            list[:class:`rez.packages_.Package`],
            list[:class:`.InvalidPackage`],
            list[:attr:`Skip`],
        ]:
            Every package that needs documentation, followed by Rez
            packages that couldn't be checked if they need documentation
            because something is wrong with the package, and lastly
            any packages that were skipped (because they already have
            documentation or some other reason).

    """
    repositories = []
    packages = []
    invalids = []
    known_issues = (
        # :func:`is_not_a_python_package` can potentially raise any of these exceptions
        rez_exceptions.PackageNotFoundError,
        rez_exceptions.ResolvedContextError,
        filesystem.PackageDefinitionFileMissing,
        # :func:`has_documentation` raises this exception
        exceptions.NoGitRepository,
    )

    for package in packages_to_report:
        if len(repositories) > maximum_repositories:
            break
        elif len(packages) > maximum_rez_packages:
            break

        try:
            repository = rez_git.get_repository_url(package)
        except (exceptions.InvalidPackage, exceptions.NoRepositoryRemote) as error:
            invalids.append(error)

            continue
        except filesystem.PackageDefinitionFileMissing as error:
            _LOGGER.exception(
                'A damaged Rez package "%s" was found. Please fix or remove it.',
                package,
                exc_info=True,
            )
            invalids.append(exceptions.InvalidPackage(package, "", str(error)))

            continue

        repositories.append(repository)
        packages.append(package)

    return packages, invalids


def run(  # pylint: disable=too-many-arguments,too-many-locals
    packages_to_run,
    command_arguments,
    maximum_repositories=sys.maxint,
    maximum_rez_packages=sys.maxint,
    paths=None,
    keep_temporary_files=False,
    temporary_directory="",
):
    """Add documentation to the given Rez packages.

    Args:
        packages_to_run (iter[:class:`rez.packages_.Package`]):
            The Rez packages to run a command on. e.g. adding documentation.
        maximum_repositories (int, optional):
            The number of unique repositories to check for packages.
            If the queried packages live in more repositories than
            this given parameter, then this function will exit early.
            Default: :attr:`sys.maxint`.
        maximum_rez_packages (int, optional):
            The number of unique Rez packages to check for
            documentation. If the queried packages live in more
            repositories than this given parameter, then this function
            will exit early. Default: :attr:`sys.maxint`.
        paths (list[str], optional):
            The locations on-disk that will be used to any
            Rez-environment-related work. Some plugins need these
            paths for resolving a context, for example. Default is None.
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
            list[:attr:`Skip`],
        ]:
            Every Rez package that was successfully "ran" by the
            command. Every Rez package did not get documentation added
            onto them. Followed by Rez packages that couldn't be checked
            if they need documentation because something is wrong with
            the package, and lastly any packages that were skipped
            (because they already have documentation or some other
            reason).

    """

    def _group_by_repository(packages):
        output = collections.defaultdict(set)

        for package in packages:
            output[rez_git.get_repository_url(package)].add(package)

        return output.items()

    packages, invalids = report(
        packages_to_run,
        maximum_repositories=maximum_repositories,
        maximum_rez_packages=maximum_rez_packages,
        paths=paths,
    )

    ran = set()
    un_ran = set()

    for repository_url, packages in _group_by_repository(packages):
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

        command = registry.get_command("shell")

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
                error = command.run(inner_repository_package, command_arguments)
            except exceptions.CoreException as error:  # pylint: disable=broad-except
                un_ran.add((inner_repository_package, error))

                continue

            if error:
                un_ran.add((inner_repository_package, error))
            else:
                ran.add(inner_repository_package)

    return ran, un_ran, invalids
