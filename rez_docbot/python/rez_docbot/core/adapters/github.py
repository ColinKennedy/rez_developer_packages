import schema

from .. import schema_type


_COMMON_TOKEN = {
    schema.Optional("authentication_type", default=schema_type.DEFAULT_AUTHENTICATION): schema.Or(
        schema_type.RAW,
        schema_type.FROM_FILE,
    ),
}
_TWO_FACTOR = {
    schema.Optional("two_factor_authentication"): schema_type.CALLABLE,
}
_USER_PASSWORD_PAIR = {
    "user": schema_type.NON_EMPTY_STR,
    "password": schema_type.NON_EMPTY_STR,
}
_USER_PASSWORD_PAIR.update(_COMMON_TOKEN)
_ACCESS_TOKEN = {
    "access_token": schema_type.NON_EMPTY_STR,  # TODO : Probably don't allow spaces here
}
_ACCESS_TOKEN.update(_COMMON_TOKEN)

_AUTHENTICATION_SCHEMA = schema.Schema(schema.Or(_USER_PASSWORD_PAIR, _ACCESS_TOKEN))


def validate(data):
    return _AUTHENTICATION_SCHEMA.validate(data)
