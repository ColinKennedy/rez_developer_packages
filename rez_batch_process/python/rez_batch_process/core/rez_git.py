#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Functions for querying git repository information from Rez packges."""

import logging
import os

import git
from git import exc
from rez_utilities import inspection

from . import exceptions

_LOGGER = logging.getLogger(__name__)


def _guess_repository_from_symlinks(directory):
    """Find a built Rez package's repository by tracing through its symlinks.

    Rez packages are frequently built using symlinks when users are
    working locally. It's not "standard-practice" for Rez work but it's
    a very common one. So, if the package is built but not released
    and no repository can be found, try to use symlinks to "find" a
    repository for that package.

    Args:
        directory (str):
            The folder to search for symlinked Rez/repositories, recursively.

    Raises:
        RuntimeError:
            If no symlinks were found or multiple Rez packages were found through symlinks.

    Returns:
        :class:`git.Repo`: The found repository.

    """
    symlinks = set()

    for root, folders, files in os.walk(directory):
        for path in folders + files:
            full = os.path.join(root, path)

            if os.path.islink(full):
                symlinks.add(full)

    if not symlinks:
        message = 'Directory "{directory}" has no symlinks.'.format(directory=directory)
        _LOGGER.debug(message)

        raise RuntimeError(message)

    packages = {inspection.get_nearest_rez_package(path).name for path in symlinks}

    if len(packages) != 1:
        raise RuntimeError(
            'More than one Rez package "{packages}" was found.'
            "".format(packages=packages)
        )

    path = next(iter(symlinks))
    real_path = os.path.realpath(os.readlink(path))

    return git.Repo(real_path, search_parent_directories=True)


def get_repository(package):
    """Get the git repository of a Rez package.

    Args:
        package (:class:`rez.packages_.Package`):
            The object that should either have a git repository defined
            or is itself inside of a git repository.

    Raises:
        :class:`.InvalidPackage`:
            If the given `package` is somehow broken.
        :class:`.exceptions.NoGitRepository:
            If `package` is not from a git repository. This usually
            happens when you install a Rez package using ``rez-pip`` or
            another automated process.

    Returns:
        :class:`git.Repo`:
            The git repository, if found. This function will either
            always return something or error out.

    """
    path = inspection.get_package_root(package)

    if not path:
        raise exceptions.InvalidPackage(package, path, "no path on-disk.")

    try:
        return git.Repo(path, search_parent_directories=True)
    except exc.InvalidGitRepositoryError:  # pylint: disable=no-member
        try:
            return _guess_repository_from_symlinks(path)
        except (
            RuntimeError,
            exc.InvalidGitRepositoryError,  # pylint: disable=no-member
        ):
            raise exceptions.NoGitRepository(
                package, path, "is not in a Git repository."
            )


def get_repository_url_from_repository(repository):
    """Get the website URL or file path from a clone git repository.

    Args:
        repository (:class:`git.Repo`):
            The repository that, presumably, has a remote URL / file path.

    Raises:
        :class:`exceptions.NoRepositoryRemote:
            The given repository has no remote URL.

    Returns:
        str: The found URL.

    """
    remotes = repository.remotes

    try:
        origin = remotes.origin
    except AttributeError:
        raise exceptions.NoRepositoryRemote(
            'No remote origin could be found for "{repository}".'.format(
                repository=repository
            )
        )

    return list(origin.urls)[0]


def get_repository_url(package):
    """Get the git repository location (url or file path) of a Rez package.

    Args:
        package (:class:`rez.packages_.Package`):
            The object that should either have a git repository defined
            or is itself inside of a git repository.

    Returns:
        str:
            The git repository url, if found. Usually, this function
            will either always return or error out.

    """
    try:
        url = package.revision["push_url"]

        # If the package was released, it should have a URL
        if url:
            return url
    except KeyError:
        # Very old Rez packages don't have push information
        raise exceptions.InvalidPackage(
            package,
            inspection.get_package_root(package),
            'Package "{package}" has no repository URL.'.format(package=package),
        )
    except (
        # Happens when `package` is not the expected type
        AttributeError,
        TypeError,
    ):
        pass

    repository = get_repository(package)

    return get_repository_url_from_repository(repository)
