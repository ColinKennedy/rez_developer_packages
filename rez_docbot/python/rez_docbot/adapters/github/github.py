"""The module responsible for connecting to `GitHub`_."""

import schema

from . import _accessor


_AUTHENTICATION_SCHEMA = schema.Schema(
    schema.Or(
        schema.Use(_accessor.UserPassword.validate),
        schema.Use(_accessor.AccessToken.validate),
    )
)


def validate(data):
    """Check if ``data`` describes `GitHub` authentication details.

    Args:
        data (dict[str, object]):
            A user / password pair, access token, or some other authentication method.

    Returns:
        TODO : Update this later.

    """
    return _AUTHENTICATION_SCHEMA.validate(data)
