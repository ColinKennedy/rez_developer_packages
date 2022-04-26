"""The main class responsible for interacting with a cloned git repository."""

import abc
import logging

import six

_LOGGER = logging.getLogger(__name__)


@six.add_metaclass(abc.ABCMeta)
class BaseRepository(object):
    """The main class responsible for interacting with a cloned git repository."""

    @abc.abstractmethod
    def add_all(self):
        """Stage every file for committing."""
        raise NotImplementedError("Implement in subclasses.")

    @abc.abstractmethod
    def checkout(self, branch):
        """Change the current branch to ``branch``.

        Create ``branch`` if it doesn't already exist.

        Args:
            branch (str): The branch to get / create. e.g. ``"gh-pages"``.

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

    def add_all(self):
        """Stage every file for committing."""
        self._clone.git.add(all=True)

    def checkout(self, branch):
        """Change the current branch to ``branch``.

        Create ``branch`` if it doesn't already exist.

        Args:
            branch (str): The branch to get / create. e.g. ``"gh-pages"``.

        """
        if branch in self._clone.branches:
            self._clone.git.checkout(branch)
        else:
            self._clone.git.checkout(b=branch)

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
        """Push all commits in the current branch to the remote."""
        _LOGGER.info(
            'Pushing from local clone "%s" to remote, "%s".',
            self.get_root(),
            self._clone.remote(),
        )

        branch = self._clone.active_branch.name
        self._clone.remote().push(branch)
