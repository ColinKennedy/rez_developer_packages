#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The main module that reports / runs some plugin command.

"__main__.py" basically wraps this module with command-line-specific
details. This module does the actual work.

"""

import collections
import logging
import operator
import os
import shutil
import sys
import tempfile

import git
from git import exc
from rez import exceptions as rez_exceptions
from rez import packages_
from rez.vendor.schema import schema
from rez_utilities import inspection, rez_configuration

from . import exceptions, rez_git
from .gitter import git_link

Skip = collections.namedtuple("Skip", "package path reason")
_LOGGER = logging.getLogger(__name__)


def _clone(url, directory):
    """Clone a Git repository listed at `url` to to some folder, `directory`.

    If `directory` is already a Git repository then load it. But if the
    directory is an invalid Git repository then re-initialize everything
    from scratch.

    Args:
        url (str):
            Some address to a Git repository or path to a local git repository.
            e.g. https://github.com/ColinKennedy/rez_developer_packages or
            git@github.com:ColinKennedy/rez_developer_packages.git or
            /some/path/to/a/cloned/rez_developer_packages.git

    Returns:
        :class:`git.Repo`: The created repository.

    """
    if os.path.isdir(directory):
        try:
            return git.Repo(directory)
        except exc.InvalidGitRepositoryError:
            _LOGGER.warning('Could not clone URL "%s" to directory "%s".', url, directory)

    return git.Repo.clone_from(url, directory)


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
                try:
                    package = packages_.get_developer_package(root)
                except IndexError:
                    # You can't access a Rez package after modifying it
                    # so if we encounter a package that was already modified
                    # in the same repository, just ignore this error.
                    #
                    # Reference: https://github.com/nerdvegas/rez/issues/857
                    #
                    # TODO : If the issue above is ever solved, remove this try/except
                    #
                    continue
                except schema.SchemaError:
                    # The package is invalid. Just skip it
                    _LOGGER.warning('Folder "%s" has an invalid Rez package.', root)

                    continue
                except rez_exceptions.PackageMetadataError:
                    # This happens in one of two scenarios:
                    # 1. The Rez package file found is invalid
                    # 2. There's a package.py file in the Rez package itself
                    #    and is being parsed as if it's a Rez package file, even though it isn't.
                    #
                    # There's not a lot that can be done about either case. So just ignore it.
                    _LOGGER.warning(
                        'Folder "%s" thought it found a Rez package but it has broken metadata. '
                        "Maybe it's not a Rez package?",
                        root,
                    )

                    continue
                except rez_exceptions.ResourceError:
                    # This happens when there's a file like package.py
                    # but it's not actually a Rez package. An error
                    # occurs because there's some kind of import in the
                    # file which Rez cannot load.
                    #
                    _LOGGER.warning(
                        'Folder "%s" contains a Rez package file which can\'t be imported. '
                        "Maybe it's not a Rez package?",
                        root,
                    )

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
    packages_to_report, maximum_repositories=sys.maxint, maximum_rez_packages=sys.maxint
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
        except exc.NoSuchPathError as error:
            # If a USD is found for `package` but it points to a file
            # location on-disk and that path does not exist.
            #
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

        return sorted(output.items(), key=operator.itemgetter(0))

    filtered_packages, invalids = report(
        packages_to_run,
        maximum_repositories=maximum_repositories,
        maximum_rez_packages=maximum_rez_packages,
    )

    ran = set()
    un_ran = set()

    for repository_url, packages in _group_by_repository(filtered_packages):
        packages = sorted(packages, key=operator.attrgetter("name"))

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

        # TODO : Replace this with ls-remote or something
        #
        # Reference: https://stackoverflow.com/a/27668138/3626104
        #
        # git ls-remote git@github.com:foo/bar.git
        # git ls-remote http://github.com/foo/bar
        #
        try:
            repository = _clone(repository_url, clone_directory)
        except exc.GitCommandError as error:
            if error.status != 128:
                # Note a permissions issue
                raise

            for package in packages:
                un_ran.add(
                    (
                        package,
                        'The Git repository "{repository_url}" failed to clone.'.format(
                            repository_url=repository_url
                        ),
                    )
                )

            continue

        repository_root = repository.working_dir

        if not keep_temporary_files:
            git_link.add_directory_to_delete(repository_root)

        for package in packages:
            definitions = list(_find_package_definitions(repository_root, package.name))

            try:
                latest = sorted(definitions, key=operator.attrgetter("version"))[-1]
            except IndexError:
                un_ran.add(
                    (
                        package,
                        'Could not find "{package.name}" in repository "{repository_root}".'
                        "".format(package=package, repository_root=repository_root),
                    )
                )

                continue

            try:
                error = runner(latest)
            except exceptions.CoreException as error:  # pylint: disable=broad-except
                un_ran.add((latest, error))

                continue
            except exc.GitCommandError as error:
                if error.status != 128:
                    # Not a permissions issue
                    raise

                un_ran.add((latest, error))

                continue
            except NotImplementedError as error:
                _LOGGER.error('Package "%s" couldn\'t be run.', latest.name)
                un_ran.add((latest, error))

                continue

            if error:
                un_ran.add((latest, error))
            else:
                ran.add(latest)

    return ran, un_ran, invalids
