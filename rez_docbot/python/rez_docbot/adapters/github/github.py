"""The module responsible for connecting to `GitHub`_."""

import schema

from .internals import accessor

_AUTHENTICATION_SCHEMA = schema.Schema(
    schema.Or(
        schema.Use(accessor.UserPassword.validate),
        schema.Use(accessor.AccessToken.validate),
    )
)


def validate(data):
    """Check if ``data`` describes `GitHub` authentication details.

    Args:
        data (dict[str, object]):
            A user / password pair, access token, or some other authentication method.

    Returns:
        Authenticator: The class meant to connect to the remote, based on ``data``.

    """
    return _AUTHENTICATION_SCHEMA.validate(data)
