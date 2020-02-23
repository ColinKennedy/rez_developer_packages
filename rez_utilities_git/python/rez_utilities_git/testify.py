#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import atexit
import contextlib
import shutil
import tempfile

from rez.config import config
from rez import packages_
from rez_utilities import inspection
import git


_REMOTES = set()


def _delete_remotes():
    for directory in _REMOTES:
        shutil.rmtree(directory)


def make_fake_repository(packages, root):
    """Create a new git repository that contains the given Rez packages.

    This function is a bit hacky. It creates a git repository, which
    is fine, but Rez packages create "in-memory" packages based on
    actual package.py files on-disk. So the packages need to copied
    to the folder where the repository was created and "re-queried"
    in order to be "true" developer Rez packages. If there was a way
    to easily create a developer Rez package, I'd do that. But meh,
    too much work.

    Args:
        packages (iter[:class:`rez.developer_package.DeveloperPackage`]):
            The Rez packages that will be copied into the new git repository.
        root (str):
            The folder on-disk that represents the top-level folder for
            every Rez package in `packages`.

    Returns:
        tuple[:class:`git.Repo`, list[:class:`rez.developer_package.DeveloperPackage`]]:
            The newly created repository + the Rez packages that got copied into it.

    """
    repository_root = os.path.join(
        tempfile.mkdtemp(suffix="_clone_repository"), "test_folder"
    )
    _REMOTES.add(repository_root)
    os.makedirs(repository_root)

    initialized_packages = []

    for package in packages:
        package_root = inspection.get_package_root(package)
        relative = os.path.relpath(package_root, root)
        destination = os.path.join(repository_root, relative)
        parent = os.path.dirname(destination)

        if not os.path.isdir(parent):
            os.makedirs(parent)

        shutil.copytree(package_root, destination)

        initialized_packages.append(packages_.get_developer_package(destination))

    remote_root = tempfile.mkdtemp(suffix="_remote_bare_repository")
    # `git.Repo.init` needs to build from a non-existent folder. So we `shutil.rmtree` here
    shutil.rmtree(remote_root)

    remote_root += ".git"  # bare repositories, by convention, end in ".git"
    _REMOTES.add(remote_root)

    remote = git.Repo.init(remote_root, bare=True)

    repository = git.Repo.init(repository_root)
    repository.index.add(
        [item for item in os.listdir(repository_root) if item != ".git"]
    )
    repository.index.commit("initial commit")
    repository.create_remote("origin", url=remote.working_dir)
    origin = repository.remotes.origin
    origin.push(refspec="master:master")
    repository.heads.master.set_tracking_branch(
        origin.refs.master
    )  # set local "master" to track remote "master

    return repository, initialized_packages, remote_root
