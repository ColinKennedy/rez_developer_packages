import abc

import six


@six.add_metaclass(abc.ABCMeta)
class Base(Exception):
    @abc.abstractmethod
    def get_error_code():
        return -1


class MissingDelimiter(Base):
    @staticmethod
    def get_error_code():
        return 1


class NoPluginFound(Base):
    @staticmethod
    def get_error_code():
        return 2
