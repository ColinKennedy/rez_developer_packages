import abc
import logging

import six


_LOGGER = logging.getLogger(__name__)


# TODO : Move this base, later
@six.add_metaclass(abc.ABCMeta)
class _Base(object):
    @abc.abstractmethod
    def add_all(self):
        raise NotImplementedError('Implement in subclasses.')

    @abc.abstractmethod
    def checkout(self, branch):
        raise NotImplementedError()

    @abc.abstractmethod
    def commit(self, message):
        raise NotImplementedError('Implement in subclasses.')

    @abc.abstractmethod
    def get_root(self):
        return ""

    @abc.abstractmethod
    def push(self):
        raise NotImplementedError('Implement in subclasses.')


class Repository(_Base):
    def __init__(self, clone, remote):
        super(Repository, self).__init__()

        self._clone = clone
        self._remote = remote

    def add_all(self):
        self._clone.git.add(all=True)

    def checkout(self, branch):
        # TODO : Double-check this. It may not work
        self._clone.git.checkout(branch)

    def commit(self, message):
        self._clone.index.commit(message)

    def get_root(self):
        return self._clone.working_dir

    def push(self):
        _LOGGER.info(
            'Pushing from local clone "%s" to remote, "%s".',
            self.get_root(),
            self._clone.remote(),
        )

        self._clone.remote().push()
