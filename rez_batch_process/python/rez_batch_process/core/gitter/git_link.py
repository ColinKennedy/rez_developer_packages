#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""A module for searching Sphinx conf.py files inside of Rez packages.

Searching for documentation in a Rez package is somewhat complex
because it's not guaranteed that a built package will come with its
documentation. Most of the time, it's in the source Rez package.

To actually search for the conf.py file(s), we **clone the repository
and search it as files, using Python**.

Important:
    All of the repositories that are cloned will be auto-cleaned by the
    :func:`_delete_temporary_repositories` function. This is to prevent
    disk space from getting filled with the temporary repositories.

Reference:
    https://stackoverflow.com/a/3850271/3626104

"""

from __future__ import print_function

import atexit
import logging
import os
import shutil
import tempfile

import git
from python_compatibility.sphinx import conf_manager
from rez import packages_
from rez_utilities import rez_configuration

try:
    from functools import lru_cache  # python 3
except ImportError:
    from backports.functools_lru_cache import lru_cache  # python 2

_DIRECTORIES_TO_DELETE = set()
_LOGGER = logging.getLogger(__name__)
_REPOSITORIES = dict()


class _ProgressBar(git.remote.RemoteProgress):
    """An object that prints repository cloning progress."""

    def update(self, op_code, cur_count, max_count=None, message=""):
        """Print the cloning progress.

        Reference:
            https://stackoverflow.com/a/38780917/3626104

        """
        _LOGGER.debug(self._cur_line)


@lru_cache(maxsize=None)
def _get_repository(url, directory="", keep=False):
    """Get a cached git repository or clone one, if it does not exist.

    Args:
        url (str):
            The website address to a git repository to clone.
        directory (str, optional):
            Part of checking for a conf.py file involves cloning the
            given `repository` to disk. If a root folder is given, the
            repository will be cloned as a child of this directory. If
            no folder is given, a temporary directory is chosen for the
            user. Default: "".
        keep (bool, optional):
            If False, delete temporary directories once they are no
            If longer needed. True, don't delete them. Default is False.

    Returns:
        :class:`git.Repo`: The created repository instance.

    """
    # TODO : Do I still need `_REPOSITORIES`? lru_cache probably already handles this.
    repository = _REPOSITORIES.get(url)

    if repository:
        return repository

    if not directory:
        directory = tempfile.mkdtemp(suffix="_temporary_test_location")
        shutil.rmtree(
            directory
        )  # Remove the folder so that we just get the folder path
    else:
        directory = make_repository_folder(directory, url)

    if not os.path.isdir(directory):
        os.makedirs(directory)
        _LOGGER.info('Now cloning repository "%s" to "%s".', url, directory)
        # TODO : Add thing to make this more quiet
        git_repository = git.Repo.clone_from(url, directory, _ProgressBar())
    else:
        _LOGGER.info('Re-using repository located at "%s".', directory)
        git_repository = git.Repo(directory)

    if not keep:
        add_directory_to_delete(directory)

    _REPOSITORIES[url] = git_repository

    return git_repository


def _delete_temporary_repositories():
    """Remove all of the cached, cloned git repositories."""
    for folder in _DIRECTORIES_TO_DELETE:
        shutil.rmtree(folder)


@lru_cache(maxsize=None)
def _iter_package_files(directory):
    """Find every Rez package file starting from a folder.

    Args:
        directory (str): The absolute path that will be used to search for Rez packages.

    Yields:
        str: The full path to any matching Rez package file.

    """
    for root, _, files in os.walk(directory):
        for path in files:
            if path in rez_configuration.REZ_PACKAGE_NAMES:
                yield os.path.join(root, path)


def has_package_conf(repository, package, directory="", keep=False):
    """Check if there is a Sphinx conf.py inside of a Rez package.

    Args:
        repository (str):
            The URL pointing to a git repository that contains `package`
            somewhere inside of it.
        package (str):
            The name of the Rez packge to find within `repository`.
        directory (str, optional):
            Part of checking for a conf.py file involves cloning the
            given `repository` to disk. If a root folder is given, the
            repository will be cloned as a child of this directory. If
            no folder is given, a temporary directory is chosen for the
            user. Default: "".
        keep (bool, optional):
            If False, delete temporary directories once they are no
            If longer needed. True, don't delete them. Default is False.

    Returns:
        bool: If a conf.py was found.

    """
    repository = _get_repository(repository, directory=directory, keep=keep)

    for path in _iter_package_files(repository.working_dir):
        name = packages_.get_developer_package(os.path.dirname(path)).name

        if name == package:
            return bool(conf_manager.get_conf_file(os.path.dirname(path)))

    return False


def add_everything_in_repository(repository):
    """Update the git repository with every modified file.

    Reference:
        https://stackoverflow.com/a/572660/3626104

    Args:
        repository (:class:`git.Repo`):
            The repository that may or may not contain files with
            un-added/un-committed changes.

    """
    repository.git.add(A=True)


def add_directory_to_delete(directory):
    """Mark a directory on-disk to delete.

    Args:
        directory (str): The absolute path to a folder on-disk
            that will be deleted once the user's Python program exits.

    """
    _DIRECTORIES_TO_DELETE.add(directory)


def make_repository_folder(directory, url):
    """Recommend a child directory within `directory` for a git repository to live in.

    Args:
        directory (str): The root URL that will be used to generate a child folder.
        url (str): The website address that contains the git repository name as a suffix.
        e.g. "https://github.com/foo/bar.git" or "https://github.com/foo/bar".

    Returns:
        str: The child folder.

    """
    # url = "https://github.com/foo/bar.git"
    repository = url.split("/")[-1]
    # repository = "bar.git"
    name = ".".join(repository.split(".")[:-1])
    # name = "bar"

    return os.path.join(directory, name)


atexit.register(_delete_temporary_repositories)
