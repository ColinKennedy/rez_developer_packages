"""An adapter class for instantiating `GitHub`_ Python classes."""

import io
import os

import github3
from git.repo import base

from ....bases import base as base_
from ....bases import repository as repository_
from ....core import exception


class GitHub(base_.Handler):
    """An adapter class for instantiating `GitHub`_ Python classes."""

    def __init__(self, handler):
        """Keep track of some `GitHub`_ API object for `CRUD`_ database purposes.

        Args:
            handler (github3.github.GitHub):
                A raw object for messing with `GitHub`_. This instance will
                wrap this object with an "expected" code interface.

        """
        super(GitHub, self).__init__()

        self._handler = handler

    def _create_repository(self, repository):
        """Make a new `GitHub`_ repository.

        Args:
            repository (str):
                The name of the repository to create under the
                current `GitHub organization`_ / user.

        Returns:
            github3.github.repos.repo.Repository: The new repository.

        """
        return self._handler.create_repository(repository)

    def _get_repository(self, details, auto_create=True):
        """Get or create a remote + cloned repository.

        Args:
            details (RepositoryDetails):
                A description of the repository full URL, the group it's nested
                under, and any other information that's important for cloning.
            auto_create (bool, optional):
                If the git repository doesn't already exist and ``auto_create``
                is True, make it and return the newly created repository.

        Raises:
            NoRemoteFound: If ``auto_create`` is False and no repository exists.

        Returns:
            github3.github.repos.repo.Repository: The found / created repository.

        """
        group = details.group
        repository = details.repository

        try:
            return self._handler.repository(group, repository)
        except github3.exceptions.NotFoundError:
            if auto_create:
                return self._create_repository(repository)

            raise exception.NoRemoteFound(
                'Group / Repository "{group} / {repository}" does not exist. '
                "Re-run with auto_create=True to fix this.".format(
                    group=group,
                    repository=repository,
                )
            )

    def apply_repository_template(self, directory):
        """Add a `.nojekyll`_ file so GitHub doesn't run CI on the current branch.

        Args:
            directory (str): The absolute path to a `git`_ repository.

        """
        _add_nojekyll_file(directory)

    def get_repository(self, details, destination, auto_create=True):
        """Get or create a remote + cloned repository.

        Args:
            details (RepositoryDetails):
                A description of the repository full URL, the group it's nested
                under, and any other information that's important for cloning.
            destination (str):
                The absolute path to a directory on-disk to clone into. This
                path should be empty.
            auto_create (bool, optional):
                If the git repository doesn't already exist and ``auto_create``
                is True, make it and return the newly created repository.

        Raises:
            RuntimeError: If ``destination`` is not empty.

        Returns:
            BaseRepository: The retrieved or created `GitHub`_ repository.

        """
        self._get_repository(details, auto_create=auto_create)

        if os.path.isdir(destination) and os.listdir(destination):
            raise RuntimeError(
                'Destination "{destination}" is not empty.'.format(
                    destination=destination,
                )
            )

        clone = base.Repo.clone_from(details.clone_url, destination)

        self.apply_repository_template(destination)

        return repository_.Repository(clone)

    def __repr__(self):
        """str: A string representation of this instance."""
        return "{self.__class__.__name__}({self._handler!r})".format(self=self)


def _add_nojekyll_file(directory):
    """Add a .nojekyll file to ``directory`` to make documentation easier.

    In `Sphinx`_, for example, there's several "_private" folders which
    `GitHub`_ would ignore by default. That's a problem, because those folders
    contain .css files and other resources.

    Adding `.nojekyll`_ ensures those files are read properly.

    Reference:
        https://github.blog/2009-12-29-bypassing-jekyll-on-github-pages

    Args:
        directory (str): The absolute path to a `git`_ repository.

    """
    nojekyll = os.path.join(directory, ".nojekyll")

    if os.path.isfile(nojekyll):
        return

    with io.open(nojekyll, "a", encoding="utf-8"):
        pass
