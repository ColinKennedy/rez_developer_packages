"""All exceptions for rez_docbot, for internal use.

These exceptions are meant just for the CLI, to give a better user experience.

"""

import abc

import six


@six.add_metaclass(abc.ABCMeta)
class Base(Exception):
    """A simple base class to inherit from, for all classes in this module."""

    @abc.abstractmethod
    def get_error_code():
        """int: A unique value to refer to this class when calling :func:`sys.exit`."""
        return -1


class NoPluginFound(Base):
    """If a user requests a plug-in and none if found, this exception gets raised."""

    @staticmethod
    def get_error_code():
        """int: A unique value to refer to this class when calling :func:`sys.exit`."""
        return 1
