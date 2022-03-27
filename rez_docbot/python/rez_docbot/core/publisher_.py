import logging
import os

import schema

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
    schema.Optional(_PUBLISH_PATTERN, default=[schema_type.DEFAULT_PUBLISH_PATTERN]): schema_type.PUBLISH_PATTERNS,
    schema.Optional(_REQUIRED, default=True): bool,
    schema.Optional(_VERSION_FOLDER, default="v"): str,  # TODO : Empty version_folder == no version folder
}
_SCHEMA = schema.Schema(_PUBLISHER)

_LOGGER = logging.getLogger(__name__)


class Publisher(object):
    def __init__(self, data):
        super(Publisher, self).__init__()

        self._data = data

    @classmethod
    def validate(cls, data):
        validated = _SCHEMA.validate(data)

        return cls(validated)

    def _get_publish_pattern_searcher(self):
        pattern = self._data[_PUBLISH_PATTERN]

        raise ValueError(pattern)

    def _get_resolved_repository_uri(self):
        base = self._data[_REPOSITORY_URI]

        return base.format(package=self._package)

    def _clone_documentation_root(self, repository):
        destination_root = _clone_repository(repository)
        inner_path = self._data[_INNER_PATH]

        if not inner_path:
            return destination_root

        directory = os.path.join(destination_root, inner_path)

        if not os.path.isdir(directory):
            os.makedirs(directory)

        return directory

    def _copy_into_latest_if_needed(self, documentation, latest, versioned):
        latest_previous_publish = self._get_latest_version_folder(versioned)

        if latest_previous_publish < self._package.version:
            _copy_into(documentation, latest)

            return

        _LOGGER.info(
            'Package "%s" is not the latest version. '
            'There is a more up-to-date version, "%s".',
            self._package,
            latest_previous_publish,
        )
        _LOGGER.info('Overwriting latest "%s" will be skipped.', latest)

    def _copy_into_versioned_if_needed(self, documentation, versioned):
        searcher = self._get_publish_pattern_searcher()

        for name in os.listdir(versioned):
            if searcher(name):
                _LOGGER.info('Existing version folder, "%s" was found.')
                return

        _copy_into(documentation, versioned)

    def authenticate(self):
        invalids = set()

        uri = self._get_resolved_repository_uri()

        for method in self._data[_AUTHENICATION]:
            handler = method.authenticate(uri)

            if handler and self._data[_REQUIRED]:
                invalids.add(method)

        if not invalids:
            raise RuntimeError('No authentication method was run.')

        raise RuntimeError('These authentication methods "{invalids}" failed.'.format(invalids=invalids))

    def quick_publish(self, documentation):
        repository = _get_repository(auto_create=True)
        root = self._clone_documentation_root(repository)

        latest = _create_directory(root, self._data[_LATEST_FOLDER])
        versioned = _create_directory(root, self._data[_VERSION_FOLDER])

        self._copy_into_latest_if_needed(documentation, latest, versioned)

        if versioned != latest:
            self._copy_into_versioned_if_needed(documentation, versioned)
        else:
            _LOGGER.warning(
                'Version folder "%s" is the same as the latest folder. '
                'To prevent publish issues, it will be skipped.',
                versioned
            )

        _add_and_commit(repository)
        _push(repository)

    def __repr__(self):
        return "{self.__class__.__name__}({self._data!r})".format(self=self)


def _copy_into(source, destination):
    _clear_directory(destination)

    raise NotImplementedError()


def _create_directory(self, root, tail):
    directory = os.path.join(root, tail)

    if not os.path.isdir(directory):
        os.makedirs(directory)

    return directory
