"""Exceptions used internally by the :ref:`rez_bisect cli`."""


class Base(Exception):
    """The class which all other exceptions inherit from."""

    pass


class BadRequest(Base):
    """A Rez :ref:`request` that has some kind of issue."""

    pass


class DuplicateContexts(Base):
    """When 2 unique Rez :ref:`contexts` are expected but only one is found."""

    pass


class FileNotFound(Base):
    """If required file was not found."""

    pass


class PermissionsError(Base):
    """If a file is missing expected permissions (read / write / execute)."""

    pass


class UserInputError(Base):
    """If the user made some kind of CLI error. e.g. a bad CLI flag."""

    pass
