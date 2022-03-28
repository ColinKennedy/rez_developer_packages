"""The main class which handles creating and publishing to git repositories."""

import logging
import os
import re
import shutil

import schema
from rez.vendor.version import version as version_

from . import adapter_registry, schema_type

_AUTHENICATION = "authentication"
_INNER_PATH = "inner_path"
_LATEST_FOLDER = "latest_folder"
_PUBLISH_PATTERN = "publish_pattern"
_REPOSITORY_URI = "repository_uri"
_REQUIRED = "required"
_VERSION_FOLDER = "version_folder"

_PUBLISHER = {
    _AUTHENICATION: schema.Use(adapter_registry.validate),
    _REPOSITORY_URI: schema.Or(
        schema_type.URL,
        # schema_type.SSH,  # TODO : Add SSH support later
    ),
    schema.Optional(_INNER_PATH): schema_type.URL_SUBDIRECTORY,
    schema.Optional(_LATEST_FOLDER, default="latest"): schema_type.NON_EMPTY_STR,
    schema.Optional(
        _PUBLISH_PATTERN, default=[schema_type.DEFAULT_PUBLISH_PATTERN]
    ): schema_type.PUBLISH_PATTERNS,
    schema.Optional(_REQUIRED, default=True): bool,
    schema.Optional(
        _VERSION_FOLDER, default="v"
    ): str,  # TODO : Empty version_folder == no version folder
}
_SCHEMA = schema.Schema(_PUBLISHER)

_LOGGER = logging.getLogger(__name__)
# Reference: https://stackoverflow.com/a/40972959/3626104
_CURLIES = re.compile(r"\{(.*?)\}")


class Publisher(object):
    """The wrapper class which interacts with the git repositories.

    It also handles cloning and pushing to remote repositories, like `GitHub`_.

    """

    def __init__(self, data):
        """Store the information related to publishing.

        The ``data`` is assumed to be already validated. See
        :meth:`Publisher.validate`.

        Args:
            data (dict[str, object]): Each git / remote data to save.

        """
        super(Publisher, self).__init__()

        self._data = data

    @classmethod
    def validate(cls, data):
        """Ensure ``data`` can be used by this class.

        Args:
            data (dict[str, object]): Each git / remote data to use.

        Returns:
            dict[str, object]: The validated content from ``data``.

        """
        validated = _SCHEMA.validate(data)

        return cls(validated)

    def _get_latest_version_folder(self, versioned):
        """Find the latest versioned folder within ``versioned``, if any.

        If ``versioned`` was just recently created, it won't have any existing
        version folders.

        Args:
            versioned (str):
                The absolute directory where all versioned documentation lives.

        Returns:
            rez.vendor.version.version.Version or NoneType:
                The found, latest version folder, if any.

        """
        searcher = self._get_publish_pattern_searcher()
        versions = [version_.Version(name) for name in os.listdir(versioned) if searcher(name)]

        if not versions:
            return None

        return max(versions)

    def _get_publish_pattern_searcher(self):
        """Get a callable function used to "find" versioned publish directories.

        Returns:
            callable[str] -> object: The found function.

        """
        # TODO : Allow _PUBLISH_PATTERN as regex, here
        pattern = self._data[_PUBLISH_PATTERN]
        temporary_token = "ctavasd"  # Some random string to replace later
        temporary_pattern = _CURLIES.sub(temporary_token, pattern)
        escaped = re.escape(temporary_pattern)

        return re.compile(escaped.replace(temporary_token, r"[\d\w]+")).match

    def _get_resolved_repository_uri(self):
        """str: Get the URL / URI / etc to a remote git repository."""
        base = self._data[_REPOSITORY_URI]

        return base.format(package=self._package)

    def _clone_documentation_root(self, repository):
        """Clone the documentation repository and get the path to the documentation.

        The documentation may be located that the root of the clone repository
        or a folder within it. If it's an inner folder, create the folder +
        return it.

        Args:
            repository TODO write this

        Returns:
            str: The created folder where all documentation for the package must go.

        """
        destination_root = _clone_repository(repository)
        inner_path = self._data[_INNER_PATH]

        if not inner_path:
            return destination_root

        inner_path = inner_path.format(package=self._package)
        directory = os.path.join(destination_root, inner_path)

        if not os.path.isdir(directory):
            os.makedirs(directory)

        return directory

    def _copy_documentation_if_needed(self, documentation, root):
        """Possibly copy the contents of ``documentation`` into ``root``.

        Whether the ``documentation`` is copied or not is dependent on these factors:

        - Is the user back-patching? If yes ...
            - make a :ref:`version folder` if one doesn't already exist
            - the :ref:`latest folder` is left un-touched
        - Does a :ref:`version folder` already exist for the package?
            - If yes, skip updating both :ref:`version folder` and :ref:`latest folder`

        So as you can see, there's no guarantee the files will be copied.

        Args:
            documentation (str):
                The absolute directory to built documentation on-disk.
            root (str):
                The absolute directory where all documentation for the current
                Rez package is expected to be copied to.

        Returns:
            bool: If any documentation was copied.

        """
        latest = _create_subdirectory(root, self._data[_LATEST_FOLDER])
        versioned = _create_subdirectory(root, self._data[_VERSION_FOLDER])

        version_copied = self._copy_into_versioned_if_needed(documentation, versioned)

        latest_copied = False

        if version_copied:
            # There's no case in which the :ref:`latest folder` would be
            # updated that didn't also require a :ref:`version folder` update.
            #
            latest_copied = self._copy_into_latest_if_needed(
                documentation, latest, versioned
            )

        return version_copied or latest_copied

    def _copy_into_latest_if_needed(self, documentation, latest, versioned):
        """Copy ``documentation`` to the :ref:`latest folder`, if needed.

        Args:
            documentation (str):
                The absolute directory to built documentation on-disk.
            latest (str):
                The absolute directory which always points to the latest Rez
                package documentation.
            versioned (str):
                The absolute directory where all versioned documentation lives.

        Returns:
            bool: If ``documentation`` was copied into the :ref:`latest folder`.

        """
        latest_previous_publish = self._get_latest_version_folder(versioned)

        if latest_previous_publish or (latest_previous_publish <= self._package.version):
            _copy_into(documentation, latest)

            return True

        _LOGGER.info(
            'Package "%s" is not the latest version. '
            'There is a more up-to-date version, "%s".',
            self._package,
            latest_previous_publish,
        )
        _LOGGER.info('Overwriting latest "%s" will be skipped.', latest)

        return False

    def _copy_into_versioned_if_needed(self, documentation, versioned):
        """Copy ``documentation`` to the :ref:`version folder`, if needed.

        Args:
            documentation (str):
                The absolute directory to built documentation on-disk.
            versioned (str):
                The absolute directory where all versioned documentation lives.

        Returns:
            bool: If ``documentation`` was copied into the :ref:`version folder`.

        """
        searcher = self._get_publish_pattern_searcher()
        package_version = searcher(str(package.version)).groups()

        for name in os.listdir(versioned):
            if searcher(name).groups() == package_version:
                _LOGGER.info('Existing version folder, "%s" was found.')

                return False

        _copy_into(documentation, versioned)

        return True

    def authenticate(self):
        """Connect this instance to the remote repository.

        Raises:
            RuntimeError: If none of the provided authentication methods succeeded.

        """
        raise NotImplementedError("Need to write this")
        invalids = set()

        uri = self._get_resolved_repository_uri()

        for method in self._data[_AUTHENICATION]:
            handler = method.authenticate(uri)

            if not handler:
                invalids.add(method)

        if not self._data[_REQUIRED]:
            raise NotImplementedError("Need to write this")

        if not invalids:
            raise RuntimeError("No authentication method was run.")

        raise RuntimeError(
            'These authentication methods "{invalids}" failed.'.format(
                invalids=invalids
            )
        )

    def quick_publish(self, documentation):
        """Clone, copy, and push ``documentation`` as required.

        Args:
            documentation (str):
                The absolute directory to built documentation on-disk.

        """
        repository = _get_repository(auto_create=True)
        root = self._clone_documentation_root(repository)

        was_copied = self._copy_documentation_if_needed(documentation, root)

        if not was_copied:
            _LOGGER.info("No documentation was updated. Skipping commit + push.")

            return

        _add_all_and_commit(repository)
        _push(repository)

    def __repr__(self):
        """str: The string representation of this instance."""
        return "{self.__class__.__name__}({self._data!r})".format(self=self)


def _copy_into(source, destination):
    """Clear ``destination`` and replace it with ``source``.

    Args:
        source (str): The absolute path to a directory to copy from.
        destination (str): The absolute path to a directory to copy / rename to.

    """
    if os.path.isdir(destination):
        shutil.rmtree(destination)

    shutil.copytree(source, destination)


def _create_subdirectory(root, tail):
    """Combine ``root`` and ``tail`` and create a directory there.

    Args:
        root (str): The absolute path to a directory to start from.
        tail (str): The subdirectory folder(s) to add onto ``root``.

    Returns:
        str: The existing / created directory.

    """
    directory = os.path.join(root, tail)

    if not os.path.isdir(directory):
        os.makedirs(directory)

    return directory
