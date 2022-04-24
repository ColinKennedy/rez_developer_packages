"""The module responsible for connecting to `GitHub`_."""

import schema

from .internals import accessor


def _validate_file_authentication(data):
    try:
        type_ = data["type"]
    except TypeError:
        raise ValueError('Data "{data!r}" is not a dict.'.format(data=data))
    except KeyError:
        raise ValueError('Data "{data!r}" must be a standard type.'.format(data=data))

    raise NotImplementedError('Need to write this', type_)


def validate(data):
    """Check if ``data`` describes `GitHub` authentication details.

    Args:
        data (dict[str, object]):
            A user / password pair, access token, or some other authentication method.

    Returns:
        Authenticator: The class meant to connect to the remote, based on ``data``.

    """
    return _AUTHENTICATION_SCHEMA.validate(data)


_STANDARD_AUTHENTICATORS = schema.Or(
    schema.Use(accessor.UserPassword.validate),
    schema.Use(accessor.AccessToken.validate),
)
_AUTHENTICATION_SCHEMA = schema.Schema(
    schema.Or(_validate_file_authentication, _STANDARD_AUTHENTICATORS),
)
