"""The module responsible for authenticating to a remote `GitHub`_ server."""

import re

import github3
import schema
from six.moves import urllib_parse

from ....bases import base
from ....core import schema_type
from . import handler

_PASSWORD = "password"
_TOKEN = "token"
_USER = "user"

_PUBLIC_GITHUB = re.compile(r"^www\.github\.com$", re.IGNORECASE)

_COMMON_TOKEN = {
    schema.Optional(
        "authentication_type", default=schema_type.DEFAULT_AUTHENTICATION
    ): schema.Or(
        schema_type.RAW,
        schema_type.FROM_FILE,
    ),
}
_COMMON_USER = {_USER: schema_type.NON_EMPTY_STR}

# TODO : Incorporate 2 factor, somehow
_TWO_FACTOR = {
    schema.Optional("two_factor_authentication"): schema_type.CALLABLE,
}

_ACCESS_TOKEN = {
    # TODO : Probably don't allow spaces in access_token
    "token": schema_type.NON_EMPTY_STR,
}
_ACCESS_TOKEN.update(_COMMON_USER)
_ACCESS_TOKEN.update(_COMMON_TOKEN)
_USER_PASSWORD_PAIR = {
    _PASSWORD: schema_type.NON_EMPTY_STR,
}
_USER_PASSWORD_PAIR.update(_COMMON_TOKEN)

_ACCESS_TOKEN_SCHEMA = schema.Schema(_ACCESS_TOKEN)
_USER_PASSWORD_PAIR_SCHEMA = schema.Schema(_USER_PASSWORD_PAIR)


class AccessToken(base.Authenticator):
    """Allow the user to authenticate with a username + `access token`_."""

    def authenticate(self, url):
        """Get a valid handle to the remote ``url``.

        Args:
            url (str):
                An addressable website. e.g. ``"https://www.github.com/Foo/bar"``
                or ``"git@github.com:Foo/bar"``

        Returns:
            Handler: The authenticated instance.

        """
        # TODO : Allow the user to read the access token from a file on-disk
        if _is_public_github(url):
            raw_handler = github3.login(
                username=self._data[_USER],
                token=self._data[_TOKEN],
            )
        else:
            raw_handler = github3.enterprise_login(
                username=self._data[_USER],
                token=self._data[_TOKEN],
                url=url,
            )

        return handler.GitHub(raw_handler)

    @classmethod
    def validate(cls, data):
        """Convert ``data`` to something this class can use.

        Args:
            data (dict[str, object]): The username / password details to store.

        Returns:
            AccessToken: The created instance.

        """
        return cls(_ACCESS_TOKEN_SCHEMA.validate(data))


class UserPassword(base.Authenticator):
    """Allow the user to authenticate with a raw username + password."""

    def authenticate(self, url):
        """Get a valid handle to the remote ``url``.

        Args:
            url (str):
                An addressable website. e.g. ``"https://www.github.com/Foo/bar"``
                or ``"git@github.com:Foo/bar"``

        Returns:
            Handler: The authenticated instance.

        """
        # TODO : Allow the user to read the password from a file on-disk
        if _is_public_github(url):
            raw_handler = github3.login(
                username=self._data[_USER],
                password=self._data[_PASSWORD],
            )
        else:
            raw_handler = github3.enterprise_login(
                username=self._data[_USER],
                password=self._data[_PASSWORD],
                url=url,
            )

        return handler.GitHub(raw_handler)

    @classmethod
    def validate(cls, data):
        """Convert ``data`` to something this class can use.

        Args:
            data (dict[str, object]): The username / password details to store.

        Returns:
            UserPassword: The created instance.

        """
        return cls(_USER_PASSWORD_PAIR_SCHEMA.validate(data))


def _is_public_github(url):
    """Check if ``url`` points to public `GitHub`_.

    Args:
        url (str):
            An addressable website. e.g. ``"https://www.github.com/Foo/bar"``
            or ``"git@github.com:Foo/bar"``

    Returns:
        bool:
            If ``url`` is an `GitHub enterprise`_ website, return False. If
            not, return True.

    """
    if url.startswith("git@github.com:"):
        # ``url`` is defined via SSH
        return True

    # ``url`` is likely a http(s) URL
    result = urllib_parse.urlparse(url)

    return bool(_PUBLIC_GITHUB.match(result.netloc))
