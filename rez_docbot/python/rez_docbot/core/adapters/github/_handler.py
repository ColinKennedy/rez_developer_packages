import github3
from git.repo import base

from ... import exception

from . import _repository


class GitHub(object):
    def __init__(self, handler):
        super(GitHub, self).__init__()

        self._handler = handler

    def _create_repository(self, repository):
        return self._handler.create_repository(repository)

    def _get_repository(self, details, auto_create=True):
        group = details.group
        repository = details.repository

        try:
            return self._handler.repository(group, repository)
        except github3.exceptions.NotFoundError:
            if auto_create:
                return self._create_repository(repository)

            raise exception.NoRepositoryFound(
                'Group / Repository "{group} / {repository}" does not exist. '
                'Re-run with auto_create=True to fix this.'.format(
                    group=group,
                    repository=repository,
                )
            )

    def get_repository(self, details, destination, auto_create=True):
        remote = self._get_repository(details, auto_create=auto_create)
        clone = base.Repo.clone_from(remote.clone_url, destination)

        return _repository.Repository(clone, remote)
