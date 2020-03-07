#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Some small wunctions for cloning temporary git repositories.

Plugins in this package tend to need to make git repositories either
for querying the Rez package data inside of them or for actually making
changes. This module helps with cloning and querying.

"""

import atexit
import functools
import logging
import os
import shutil
import sys
import tempfile

import git
from rez import exceptions as rez_exceptions
from rez import packages_
from rez_batch_process import cli
from rez_utilities import inspection
from rez_utilities_git import gitter

_LOGGER = logging.getLogger(__name__)


def _is_keep_temporary_files_enabled():
    """bool: Check if the user asked to not delete auto-generated files."""
    arguments, _ = cli.parse_arguments(sys.argv[1:])

    return arguments.keep_temporary_files


def _get_repository_name(uri):
    """str: Get the name that a Git repository will be called once it's cloned to-disk."""
    base = uri.split("/")[-1]

    if base.endswith(".git"):
        base = base[: -1 * len(".git")]

    return base


def _get_temporary_directory():
    """str: Get the directory used for cloning Rez repositories to-disk."""
    arguments, _ = cli.parse_arguments(sys.argv[1:])

    return arguments.temporary_directory or tempfile.mkdtemp(
        suffix="_some_location_to_clone_repositories"
    )


def is_definition(package, format_):
    """Check if the given package defines a Rez package file.

    Args:
        package (:class:`rez.packages_.DeveloperPackage`):
            A package on-disk that will be verified.
        format_ (:attr:`rez.serialise.FileFormat`):
            A file format to query with. e.g.
            `rez.serialise.FileFormat.yaml` or
            `rez.serialise.FileFormat.py`.

    Returns:
        bool: If `package` defines a package.py, return True. Otherwise, return False.

    """
    def _is_definition(package, format_, search=True):
        """Check for if a package defines a Rez package file.

        Except if we've already checked the Rez package's repository
        and still haven't found a good answer, stop searching and just
        return False, to avoid a cyclic loop.

        """
        if not inspection.is_built_package(package):
            path = inspection.get_package_root(package)

            try:
                packages_.get_developer_package(path, format=format_)
            except rez_exceptions.PackageMetadataError:
                return False

            return True

        if not search:
            return False

        repository = get_repository(package)
        repository_package = get_package(repository.working_dir, package.name)

        return _is_definition(repository_package, format_=format_, search=False)

    return _is_definition(package, format_, search=True)


def get_package(directory, name):
    """Find the Rez package within some directory matching the given name.

    Args:
        directory (str):
            The absolute path to some folder on-disk which contains Rez packages.
        name (str):
            A Rez package family that will be searched.

    Returns:
        :class:`rez.packages_.DeveloperPackage` or NoneType: The found package, if any.

    """
    def _get_version(package):
        try:
            return package.version
        except Exception:  # pylint: disable=broad-except
            return -1

    definitions = set()

    for package in inspection.get_all_packages(directory):
        try:
            name_ = package.name
        except Exception:  # pylint: disable=broad-except
            _LOGGER.warning('Package "%s" has no name.', package)

            continue

        if name_ == name:
            definitions.add(package)

    try:
        return sorted(definitions, key=_get_version)[-1]
    except IndexError:
        return None


def get_repository(package):
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
