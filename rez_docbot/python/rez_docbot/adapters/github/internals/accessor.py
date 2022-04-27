"""The module responsible for authenticating to a remote `GitHub`_ server."""

import re

import github3
import schema
from six.moves import urllib_parse

from ....bases import base
from ....core import exception, schema_type
from . import handler

_PASSWORD = "password"
_TOKEN = "token"
_USER = "user"

_PUBLIC_GITHUB = re.compile(r"^www\.github\.com$", re.IGNORECASE)
_PUBLIC_GITHUB_SSH = "git@github.com:"

_COMMON_USER = {_USER: schema_type.NON_EMPTY_STR}

_ACCESS_TOKEN = {"token": schema_type.GITHUB_ACCESS_TOKEN}
_ACCESS_TOKEN.update(_COMMON_USER)
_USER_PASSWORD_PAIR = {
    _PASSWORD: schema_type.NON_EMPTY_STR,
}

_ACCESS_TOKEN_SCHEMA = schema.Schema(_ACCESS_TOKEN)
_USER_PASSWORD_PAIR_SCHEMA = schema.Schema(_USER_PASSWORD_PAIR)


class AccessToken(base.Authenticator):
    """Allow the user to authenticate with a username + `GitHub access token`_."""

    def authenticate(self, uri):
        """Get a valid handle to the remote ``uri``.

        Args:
            uri (str):
                An addressable website. e.g. ``"https://www.github.com/Foo/bar"``
                or ``"git@github.com:Foo/bar"``

        Raises:
            NoRemoteFound:
                When bad user / token data is given, resulting in some unhandled error.

        Returns:
            Handler: The authenticated instance.

        """
        if _is_public_github(uri):
            raw_handler = github3.login(
                username=self._data[_USER],
                token=self._data[_TOKEN],
            )
        else:
            raw_handler = github3.enterprise_login(
                username=self._data[_USER],
                token=self._data[_TOKEN],
                url=uri,
            )

        if not raw_handler:
            raise exception.NoRemoteFound("No remote handler could be found.")

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

    def authenticate(self, uri):
        """Get a valid handle to the remote ``uri``.

        Args:
            uri (str):
                An addressable website. e.g. ``"https://www.github.com/Foo/bar"``
                or ``"git@github.com:Foo/bar"``

        Returns:
            Handler: The authenticated instance.

        """
        if _is_public_github(uri):
            raw_handler = github3.login(
                username=self._data[_USER],
                password=self._data[_PASSWORD],
            )
        else:
            raw_handler = github3.enterprise_login(
                username=self._data[_USER],
                password=self._data[_PASSWORD],
                url=uri,
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
            If ``url`` is an `GitHub Enterprise`_ website, return False. If
            not, return True.

    """
    if url.startswith(_PUBLIC_GITHUB_SSH):
        # ``url`` is defined via SSH
        return True

    # ``url`` is likely a http(s) URL
    result = urllib_parse.urlparse(url)

    return bool(_PUBLIC_GITHUB.match(result.netloc))
