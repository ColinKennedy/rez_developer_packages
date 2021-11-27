"""Any classes / functions needed for implementing a custom build plug-in."""

import abc

import six


@six.add_metaclass(abc.ABCMeta)
class BuilderPlugin(object):
    """An abstract class which users inherit and implement for builder plug-ins."""

    @abc.abstractmethod
    def get_name():
        """str: The name used to refer to this plug-in."""
        return ""

    @staticmethod
    @abc.abstractmethod
    def build(namespace):
        pass

    @staticmethod
    @abc.abstractmethod
    def parse_arguments(text):
        pass
