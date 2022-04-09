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


class DoesNotExist(Base):
    """If something required is missing (This exception is intentionally vague)."""

    exit_code = GENERIC_EXIT_CODE + 35


class PackageConflict(Base):
    """When only 1 unique Rez package family name is expected but multiple are found."""

    exit_code = GENERIC_EXIT_CODE + 40


class PluginConfigurationError(ConfigurationError):
    """If :ref:`rez_docbot` is enabled but the user is missing configuration data."""

    exit_code = GENERIC_EXIT_CODE + 42


class PermissionError(ConfigurationError):
    """When an expected file / folder needs to be readable, but is not."""

    exit_code = GENERIC_EXIT_CODE + 43


class MissingPlugIn(Base):
    """If a plug-in (like :ref:`rez_docbot <rez_docbot>`) could not be loaded."""

    exit_code = GENERIC_EXIT_CODE + 45


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


class RezSphinxException(Base):
    """If somehow :ref:`rez_sphinx`'s code diverges in an unexpected way.

    Example:
        The :func:`.preprocess_entry_point.run` function is renamed but
        :func:`.preference.validate_help_settings` isn't updated to
        reflect that change.

    If this exception occurs, it's always a maintainer error that must be fixed
    on :ref:`rez_sphinx`'s code.

    """

    exit_code = GENERIC_EXIT_CODE + 90


class SphinxConfError(Base):
    """When the user's `Sphinx conf.py`_ is unreadable or has empty content."""

    exit_code = GENERIC_EXIT_CODE + 100


class SphinxExecutionError(Base):
    """If some `Sphinx`_ CLI program fails to run and stops midway."""

    exit_code = GENERIC_EXIT_CODE + 110


class UserInputError(Base):
    """If a user argument to the CLI or `rez-config`_ is not allowed."""

    exit_code = GENERIC_EXIT_CODE + 120
