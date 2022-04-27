"""The main class responsible for interacting with a cloned git repository."""

import abc
import logging

import six
from git import exc

from ..core import exception

_LOGGER = logging.getLogger(__name__)


@six.add_metaclass(abc.ABCMeta)
class BaseRepository(object):
    """The main class responsible for interacting with a cloned git repository."""

    @abc.abstractmethod
    def has_branch(self, branch):
        """Check if ``branch`` exists in this instance.

        Args:
            branch (str): The local or remote branch to query.

        Returns:
            bool: If the branch is found, return True.

        """
        return False

    @abc.abstractmethod
    def is_ready_to_commit(self):
        """bool: Check if this repository should be committed + pushed."""
        return False

    @abc.abstractmethod
    def add_all(self):
        """Stage every file for committing."""
        raise NotImplementedError("Implement in subclasses.")

    @abc.abstractmethod
    def checkout(self, branch, create=False):
        """Change the current branch to ``branch``.

        Create ``branch`` if it doesn't already exist.

        Args:
            branch (str): The branch to get / create. e.g. ``"gh-pages"``.
            create (bool, optional): If True, create the ``branch`` as well.

        """
        raise NotImplementedError()

    @abc.abstractmethod
    def commit(self, message):
        """Commit all staged changes with a new commit, containing ``message``.

        Args:
            message (str): The description of the commits changes.

        """
        raise NotImplementedError("Implement in subclasses.")

    @abc.abstractmethod
    def get_root(self):
        """str: The absolute directory to where this repository was cloned to."""
        return ""

    @abc.abstractmethod
    def push(self):
        """Push all commits in the current branch to the remote."""
        raise NotImplementedError("Implement in subclasses.")


class Repository(BaseRepository):
    """A basic wrapper for detailing with git repositories.

    It should work for any git repository coming from any remote. But this
    class may need to be further specialized in the future.

    """

    def __init__(self, repository):
        """Keep track of a cloned repository to edit and query later.

        Args:
            repository (git.repo.base.Repo): The cloned repository on-disk to track.

        """
        super(Repository, self).__init__()

        self._clone = repository

    def has_branch(self, branch):
        """Check if ``branch`` exists in this instance.

        Args:
            branch (str): The local or remote branch to query.

        Returns:
            bool: If the branch is found, return True.

        """
        return branch in self._clone.branches

    def is_ready_to_commit(self):
        """bool: Check if this repository should be committed + pushed."""
        # Reference: https://stackoverflow.com/a/40509040/3626104
        if not self._clone.is_dirty(untracked_files=True):
            # If there's unstaged changes
            return False

        # Reference: https://stackoverflow.com/a/4855096/3626104
        untracked_files = self._clone.ls_files(exclude_standard=True, others=True)

        if untracked_files:
            # If there are unstaged files, we shouldn't commit yet.
            return False

        return True

    def add_all(self):
        """Stage every file for committing."""
        self._clone.git.add(all=True)

    def checkout(self, branch, create=False):
        """Change the current branch to ``branch``.

        Args:
            branch (str): The branch to get / create. e.g. ``"gh-pages"``.
            create (bool, optional): If True, create the ``branch`` as well.

        """
        if create and not self.has_branch(branch):
            self._clone.git.checkout(b=branch)  # Create + checkout

            return

        self._clone.git.checkout(branch)

    def commit(self, message):
        """Commit all staged changes with a new commit, containing ``message``.

        Args:
            message (str): The description of the commits changes.

        """
        self._clone.index.commit(message)

    def get_root(self):
        """str: The absolute directory to where this repository was cloned to."""
        return self._clone.working_dir

    def push(self):
        """Push all commits in the current branch to the remote.

        Raises:
            RemoteActionFailed: If we could not push to the remote.

        """
        _LOGGER.info(
            'Pushing from local clone "%s" to remote, "%s".',
            self.get_root(),
            self._clone.remote(),
        )

        branch = self._clone.active_branch.name
        remote = self._clone.remote()

        try:
            remote.push(branch)
        except exc.GitError:
            _LOGGER.exception("Cannot push")

            raise exception.RemoteActionFailed(
                'Remote "{remote}" could not be pushed to.'.format(remote=remote)
            )
