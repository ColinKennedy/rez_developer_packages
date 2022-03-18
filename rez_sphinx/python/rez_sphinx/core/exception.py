"""All exceptions needed by :ref:`rez_sphinx` for internal use.

These exceptions are not meant for any third-party package to import or use.

"""

GENERIC_EXIT_CODE = 1


class Base(Exception):
    """A class which all exceptions in this module must inherit from."""

    exit_code = GENERIC_EXIT_CODE + 1


class ConfigurationError(Base):
    """If the user's rez-config would prevent :ref:`rez_sphinx` from running."""

    exit_code = GENERIC_EXIT_CODE + 2


class NoDocumentationFound(Base):
    """If source documentation is required for something, but is missing."""

    exit_code = GENERIC_EXIT_CODE + 3


class NoDocumentationWritten(Base):
    """If source documentation is required for something, but is missing."""

    exit_code = GENERIC_EXIT_CODE + 4


class NoPackageFound(Base):
    """If a Rez package is needed but none can be found."""

    exit_code = GENERIC_EXIT_CODE + 5


class NoPythonFiles(Base):
    """If at least one Python file was needed but none were found."""

    exit_code = GENERIC_EXIT_CODE + 6


class SphinxExecutionError(Base):
    """If some `Sphinx`_ CLI program fails to run and stops midway."""

    exit_code = GENERIC_EXIT_CODE + 7


class UserInputError(Base):
    """If a user argument to the CLI or `rez-config`_ is not allowed."""

    exit_code = GENERIC_EXIT_CODE + 8
