"""All exceptions needed by :ref:`rez_sphinx` for internal use.

These exceptions are not meant for any third-party package to import or use.

"""

GENERIC_EXIT_CODE = 1


class Base(Exception):
    """A class which all exceptions in this module must inherit from."""

    exit_code = GENERIC_EXIT_CODE + 10


class BadPackage(Base):
    """If a valid Rez package (e.g. package.py) is expected but not found."""

    exit_code = GENERIC_EXIT_CODE + 20


class ConfigurationError(Base):
    """If the user's rez-config would prevent :ref:`rez_sphinx` from running."""

    exit_code = GENERIC_EXIT_CODE + 30


class PackageConflict(Base):
    """When only 1 unique Rez package family name is expected but multiple are found."""

    exit_code = GENERIC_EXIT_CODE + 40


class NoDocumentationFound(Base):
    """If source documentation is required for something, but is missing."""

    exit_code = GENERIC_EXIT_CODE + 50


class NoDocumentationWritten(Base):
    """If source documentation is required for something, but is missing."""

    exit_code = GENERIC_EXIT_CODE + 60


class NoPackageFound(Base):
    """If a Rez package is needed but none can be found."""

    exit_code = GENERIC_EXIT_CODE + 70


class NoPythonFiles(Base):
    """If at least one Python file was needed but none were found."""

    exit_code = GENERIC_EXIT_CODE + 80


class SphinxConfError(Base):
    """When the user's `Sphinx conf.py`_ is unreadable or has empty content."""

    exit_code = GENERIC_EXIT_CODE + 100


class SphinxExecutionError(Base):
    """If some `Sphinx`_ CLI program fails to run and stops midway."""

    exit_code = GENERIC_EXIT_CODE + 110


class UserInputError(Base):
    """If a user argument to the CLI or `rez-config`_ is not allowed."""

    exit_code = GENERIC_EXIT_CODE + 120
