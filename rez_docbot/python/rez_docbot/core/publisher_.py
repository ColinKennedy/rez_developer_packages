import schema

from . import adapter_registry, schema_type

_AUTHENICATION = "authentication"
_REPOSITORY_URI = "repository_uri"
_REQUIRED = "required"

_PUBLISHER = {
    _AUTHENICATION: schema.Use(adapter_registry.validate),
    _REPOSITORY_URI: schema.Or(
        schema_type.URL,
        # schema_type.SSH,  # TODO : Add SSH support later
    ),
    schema.Optional("inner_path"): schema_type.URL_SUBDIRECTORY,
    schema.Optional("latest_folder", default="latest"): schema_type.NON_EMPTY_STR,
    schema.Optional("publish_pattern", default=[schema_type.DEFAULT_PUBLISH_PATTERN]): schema_type.PUBLISH_PATTERNS,
    schema.Optional(_REQUIRED, default=True): bool,
    schema.Optional("version_folder", default="v"): str,  # TODO : Empty version_folder == no version folder
}
_SCHEMA = schema.Schema(_PUBLISHER)


class Publisher(object):
    def __init__(self, data):
        super(Publisher, self).__init__()

        self._data = data

    @classmethod
    def validate(cls, data):
        validated = _SCHEMA.validate(data)

        return cls(validated)

    def authenticate(self):
        invalids = set()

        uri = self._data[_REPOSITORY_URI]

        for method in self._data[_AUTHENICATION]:
            handler = method.authenticate(uri)

            if handler and method[_REQUIRED]:
                invalids.add(method)

        if not invalids:
            raise RuntimeError('No authentication method was run.')

        raise RuntimeError('These authentication methods "{invalids}" failed.'.format(invalids=invalids))

    def __repr__(self):
        return "{self.__class__.__name__}({self._data!r})".format(self=self)
