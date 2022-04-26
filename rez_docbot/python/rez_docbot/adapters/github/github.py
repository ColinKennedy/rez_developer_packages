"""The module responsible for connecting to `GitHub`_."""

import schema

from ...core import schema_type
from .internals import accessor

_PAYLOAD_KEY = "payload"
_TYPE_KEY = "type"


def _validate_file_authentication(data):
    """Read the authentication data from a file on-disk.

    Args:
        data (dict[str, str]):
            The expected file payload to read.  e.g. ``{"type":
            "from_json_path", "payload": "/some/path.json"}``.  This payload
            can have anything inside of it, as long as it's supported by
            :func:`validate`. And yes, nested payloads are supported.

    Returns:
        Authenticator: The class meant to connect to the remote, based on ``data``.

    """
    validated = _FROM_JSON_SCHEMA.validate(data)

    authenticators = schema.Schema(_STANDARD_AUTHENTICATORS)
    payload = validated[_PAYLOAD_KEY]

    return authenticators.validate(payload)


def validate(data):
    """Check if ``data`` describes `GitHub` authentication details.

    Args:
        data (dict[str, object]):
            A user / password pair, access token, or some other authentication method.

    Returns:
        Authenticator: The class meant to connect to the remote, based on ``data``.

    """
    return _AUTHENTICATION_SCHEMA.validate(data)


_FROM_JSON_SCHEMA = schema.Schema(
    {
        _TYPE_KEY: "from_json_path",
        _PAYLOAD_KEY: schema_type.JSON_FILE_PATH,
    }
)
_STANDARD_AUTHENTICATORS = schema.Or(
    schema.Use(accessor.UserPassword.validate),
    schema.Use(accessor.AccessToken.validate),
)
_AUTHENTICATION_SCHEMA = schema.Schema(
    schema.Or(schema.Use(_validate_file_authentication), _STANDARD_AUTHENTICATORS),
)
