import six


_COMMA_SEPARATOR = ","
_QUOTES = ('"', "'")


def _validate_non_zero(value):
    if not isinstance(value, int):
        raise ValueError('Item "{value}" is not an integer!'.format(value=value))

    if value != 0:
        return value

    raise ValueError('Value "{value}" cannot be 0.'.format(value=value))


def _unquote(text):
    if text.startswith(_QUOTES):
        text = text[1:]

    if text.endswith(_QUOTES):
        text = text[:-1]

    return text


def _validate_comma_separated_list(value):
    if not isinstance(value, six.string_types):
        raise ValueError('Item "{value!r}" is not a string.'.format(value=value))

    value = _unquote(value)

    return value.split(_COMMA_SEPARATOR)


def _validate_hex(value):
    if not isinstance(value, six.string_types):
        raise ValueError('Item "{value!r}" is not a string.'.format(value=value))

    value = _unquote(value)

    if not value.startswith("#"):
        raise ValueError('String "{value}" is not a HEX string. e.g. "#111111".'.format(value=value))

    return value


NON_ZERO = _validate_non_zero
HEX = _validate_hex
STYLE = _validate_comma_separated_list
