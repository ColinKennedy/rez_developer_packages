"""All exceptions needed by :ref:`rez_sphinx` for internal use.

These exceptions are not meant for any third-party package to import or use.

"""


class Base(Exception):
    """A class which all exceptions in this module must inherit from."""

    pass


class UserInputError(Base):
    """If the user provided something to the CLI or :ref:`rez-config` which is not allowed."""

    pass


class NoPackageFound(Base):
    """If a Rez package is needed but none can be found."""

    pass
