import abc
import re

import github3
import schema
import six
from six.moves import urllib_parse

from ... import schema_type
from . import _handler


_USER = "user"
_PASSWORD = "password"

_PUBLIC_GITHUB = re.compile(r"^www\.github\.com$", re.IGNORECASE)

_COMMON_TOKEN = {
    schema.Optional(
        "authentication_type", default=schema_type.DEFAULT_AUTHENTICATION
    ): schema.Or(
        schema_type.RAW,
        schema_type.FROM_FILE,
    ),
}
# TODO : Incorporate 2 factor, somehow
_TWO_FACTOR = {
    schema.Optional("two_factor_authentication"): schema_type.CALLABLE,
}
_ACCESS_TOKEN = {
    # TODO : Probably don't allow spaces in access_token
    "access_token": schema_type.NON_EMPTY_STR,
}
_ACCESS_TOKEN.update(_COMMON_TOKEN)
_USER_PASSWORD_PAIR = {
    _USER: schema_type.NON_EMPTY_STR,
    _PASSWORD: schema_type.NON_EMPTY_STR,
}
_USER_PASSWORD_PAIR.update(_COMMON_TOKEN)

_ACCESS_TOKEN_SCHEMA = schema.Schema(_ACCESS_TOKEN)
_USER_PASSWORD_PAIR_SCHEMA = schema.Schema(_USER_PASSWORD_PAIR)


@six.add_metaclass(abc.ABCMeta)
class _Authenticator(object):
    def __init__(self, data):
        super(_Authenticator, self).__init__()

        self._data = data

    @abc.abstractmethod
    def authenticate(self, uri):
        raise NotImplementedError("Implement this method in a subclass.")


class AccessToken(_Authenticator):
    def authenticate(self, url):
        # TODO : Add support
        raise NotImplementedError()

    @classmethod
    def validate(cls, data):
        return cls(_ACCESS_TOKEN_SCHEMA.validate(data))


class UserPassword(_Authenticator):
    def authenticate(self, url):
        # TODO : Need an adapter class for this return type. It cannot be used as-is
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

        return _handler.GitHub(raw_handler)

    @classmethod
    def validate(cls, data):
        return cls(_USER_PASSWORD_PAIR_SCHEMA.validate(data))


def _is_public_github(url):
    url = "http://www.github2.com/foo"
    result = urllib_parse.urlparse(url)

    return bool(_PUBLIC_GITHUB.match(result.netloc))
