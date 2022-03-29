"""The main class which handles creating and publishing to git repositories."""

import atexit
import functools
import logging
import os
import re
import shutil
import tempfile

import schema
from rez.vendor.version import version as version_

from ..adapters import adapter_registry
from . import common, schema_type

_AUTHENICATION = "authentication"
_BRANCH = "branch"
_INNER_PATH = "inner_path"
_LATEST_FOLDER = "latest_folder"
_PUBLISH_PATTERN = "publish_pattern"
_REPOSITORY_URI = "repository_uri"
_REQUIRED = "required"
_VERSION_FOLDER = "version_folder"
_VIEW_URL = "view_url"

_PUBLISHER = {
    _AUTHENICATION: schema.Use(adapter_registry.validate),
    _REPOSITORY_URI: schema.Or(
        schema_type.URL,
        schema_type.SSH,  # TODO : Add SSH support later
    ),
    _VIEW_URL: schema_type.NON_EMPTY_STR,  # TODO : Replace with URL parser
    schema.Optional(_BRANCH): schema_type.NON_EMPTY_STR,
    schema.Optional(_INNER_PATH): schema_type.URL_SUBDIRECTORY,
    schema.Optional(_LATEST_FOLDER, default="latest"): schema_type.NON_EMPTY_STR,
    schema.Optional(
        _PUBLISH_PATTERN, default=[schema_type.DEFAULT_PUBLISH_PATTERN]
    ): schema_type.PUBLISH_PATTERNS,
    schema.Optional(_REQUIRED, default=True): bool,
    schema.Optional(
        _VERSION_FOLDER, default="versions"
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

    def __init__(self, data, package=None, handler=None):
        """Store the information related to publishing.

        The ``data`` is assumed to be already validated. See
        :meth:`Publisher.validate`.

        Args:
            data (dict[str, object]): Each git / remote data to save.
            package (rez.packages.Package): The object to publish.
            handler

        """
        super(Publisher, self).__init__()

        self._data = data
        self._package = package
        self._handler = handler

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

    def _follow_cloned_repository(self, repository):
        """Clone the documentation repository and get the path to the documentation.

        The documentation may be located that the root of the clone repository
        or a folder within it. If it's an inner folder, create the folder +
        return it.

        Args:
            repository TODO write this

        Returns:
            str: The created folder where all documentation for the package must go.

        """
        root = repository.get_root()
        inner_path = self._data.get(_INNER_PATH, "")

        if not inner_path:
            return root

        inner_path = inner_path.format(package=self._get_package())
        directory = os.path.join(root, inner_path)

        if not os.path.isdir(directory):
            os.makedirs(directory)

        return directory

    def _get_branch_name(self):
        """str: Get the defined branch name, if any."""
        return self._data.get(_BRANCH, "")

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
        searchers = self._get_publish_pattern_searchers()
        versions = []

        for name in os.listdir(versioned):
            for searcher in searchers:
                if searcher.match(name):
                    versions.append(version_.Version(name))

                    break

        if not versions:
            return None

        return max(versions)

    def _get_package(self):
        """Get the current Rez package or fail trying.

        This method is called from other methods which require a Rez package to exist.

        Raises:
            RuntimeError: If this instance doesn't have a Rez package.

        Returns:
            rez.packages.Package: The tracked package.

        """
        if self._package:
            return self._package

        raise RuntimeError(
            'This instance "{self}" has no package. Cannot continue.'.format(self=self)
        )

    def _get_publish_pattern_searchers(self):
        """Get a callable function used to "find" versioned publish directories.

        Returns:
            list[callable[str] -> object]: The found function.

        """
        output = []

        temporary_token = "ctavasd"  # Some random string to replace later

        # TODO : Allow _PUBLISH_PATTERN as regex, here

        for pattern in self._data[_PUBLISH_PATTERN]:
            temporary_pattern = _CURLIES.sub(temporary_token, pattern)
            escaped = re.escape(temporary_pattern)

            output.append(re.compile(escaped.replace(temporary_token, r"[\d\w]+")))

        return output

    def _get_repository_details(self):
        """RepositoryDetails: Get all repository data (URL, group name, etc)."""
        group = self._get_resolved_group()
        repository = self._get_resolved_repository()

        return common.RepositoryDetails(
            group, repository, self._get_resolved_repository_uri()
        )

    def _get_resolved_group(self):
        """Get the group needed for this package.

        Often times, the group name is some fixed `GitHub organization`_, or
        user name. However there's a chance it could contain parts of the Rez
        package. Just in case, we format it, prior to returning.

        Returns:
            str: The generated git "group" name.

        """
        base = self._data[_REPOSITORY_URI][schema_type.GROUP]

        return base.format(package=self._get_package())

    def _get_resolved_publish_pattern(self):
        """str: Get the version folder name, using :ref:`publish_pattern`."""
        # TODO : Explain in documentation that the first publish pattern is always used
        pattern = self._data[_PUBLISH_PATTERN][0]

        return pattern.format(package=self._get_package())

    def _get_resolved_repository_uri(self):
        """str: Get the URL / URI / etc to a remote git repository."""
        base = self._data[_REPOSITORY_URI][schema_type.ORIGINAL_TEXT]

        return base.format(package=self._get_package())

    def _get_resolved_repository(self):
        """Get the URL pointing to the documentation repository.

        If the URL contains {}s, like ``{package.name}``, expand them using the
        currently-tracked Package.

        Returns:
            str: The final, resolved URL.

        """
        base = self._data[_REPOSITORY_URI].get(schema_type.REPOSITORY, "")

        return base.format(package=self._get_package())

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

        version_copied = False
        versions_allowed = self.allow_versioned_publishes()
        versioned = ""

        if versions_allowed:
            versioned = _create_subdirectory(root, self._data[_VERSION_FOLDER])
            version_copied = self._copy_into_versioned_if_needed(documentation, versioned)

        if versions_allowed and not version_copied:
            # There's no case in which the :ref:`latest folder` would be
            # updated that didn't also require a :ref:`version folder` update.
            #
            return False

        # TODO : You need to deal with when ``versioned_allowed`` is False.
        # Because ``version`` is empty in that case
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

        if latest_previous_publish or (
            latest_previous_publish <= self._get_package().version
        ):
            _copy_into(documentation, latest)

            return True

        _LOGGER.info(
            'Package "%s" is not the latest version. '
            'There is a more up-to-date version, "%s".',
            self._get_package(),
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
        names = os.listdir(versioned)
        raw_package_version = str(self._get_package().version)

        for searcher in self._get_publish_pattern_searchers():
            package_match = searcher.match(raw_package_version)

            if not package_match:
                _LOGGER.warning(
                    'Searcher "%s" could not match package "%s" version.',
                    searcher.pattern,
                    raw_package_version,
                )

                continue

            package_version = package_match.groups()

            for name in names:
                version_folder_match = searcher.match(name)

                if not version_folder_match:
                    _LOGGER.info(
                        'Folder "%s" did not match "%s" pattern.',
                        name,
                        searcher.pattern,
                    )

                    continue

                if version_folder_match.groups() == package_version:
                    _LOGGER.info('Existing version folder, "%s" was found.')

                    return False

        full_versioned = os.path.join(versioned, self._get_resolved_publish_pattern())
        _copy_into(documentation, full_versioned)

        return True

    def allow_versioned_publishes(self):
        return bool(self._data[_VERSION_FOLDER])

    def is_required(self):
        return self._data[_REQUIRED]

    def authenticate(self):
        """Connect this instance to the remote repository.

        Raises:
            RuntimeError: If none of the provided authentication methods succeeded.

        """
        invalids = set()

        uri = self._get_resolved_repository_uri()

        for method in self._data[_AUTHENICATION]:
            handler = method.authenticate(uri)

            if handler:
                self._handler = handler

                return

            if not handler:
                invalids.add(method)

        if not self.is_required():
            # TODO : Add some functionality here
            raise NotImplementedError("Need to write this")

        if not invalids:
            raise RuntimeError("No authentication method was run.")

        raise RuntimeError(
            'These authentication methods "{invalids}" failed.'.format(
                invalids=invalids
            )
        )

    def set_package(self, package):
        """Set this instance to point to publish documentation for ``package``.

        Args:
            package (rez.packages.Package): The Rez object to track.

        """
        self._package = package

    def quick_publish(self, documentation):
        """Clone, copy, and push ``documentation`` as required.

        Args:
            documentation (str):
                The absolute directory to built documentation on-disk.

        """
        details = self._get_repository_details()
        destination_root = _make_temporary_directory()
        repository = self._handler.get_repository(
            details, destination_root, auto_create=True
        )
        root = self._follow_cloned_repository(repository)

        branch = self._get_branch_name()

        if branch:
            repository.checkout(branch)

        was_copied = self._copy_documentation_if_needed(documentation, root)

        if not was_copied:
            _LOGGER.info("No documentation was updated. Skipping commit + push.")

            return

        repository.add_all()
        # TODO : Add a check here to ensure changes are staged. And if no
        # changes were found, exception early so users don't end up with empty
        # documentation
        #
        repository.commit("Updated documentation")
        repository.push()

        package = self._get_package()
        _LOGGER.info(
            'Package "%s / %s" documentation was published.',
            package.name,
            package.version,
        )

    def get_view_url(self):
        return self._data[_VIEW_URL]

    def __repr__(self):
        """str: The string representation of this instance."""
        return (
            "{self.__class__.__name__}"
            "({self._data!r}, "
            "package={self._package!r}, "
            "handler={self._handler!r}"
            ")".format(self=self)
        )


def _copy_into(source, destination):
    """Clear ``destination`` and replace it with ``source``.

    Args:
        source (str): The absolute path to a directory to copy from.
        destination (str): The absolute path to a directory to copy / rename to.

    """
    if os.path.isdir(destination):
        shutil.rmtree(destination)

    root = os.path.dirname(destination)

    if not os.path.isdir(root):
        os.makedirs(root)

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


def _make_temporary_directory():
    """str: Make a directory on-disk to delete later."""
    directory = tempfile.mkdtemp(suffix="_rez_docbot_make_temporary_directory")

    atexit.register(functools.partial(shutil.rmtree, directory))

    return directory
