import six


_COMMA_SEPARATOR = ","
_QUOTES = ('"', "'")


def _unquote(text):
    if text.startswith(_QUOTES):
        text = text[1:]

    if text.endswith(_QUOTES):
        text = text[:-1]

    return text


def _validate_comma_separated_list(value):
    value = _validate_label_text(value)

    return value.split(_COMMA_SEPARATOR)


def _validate_label_text(value):
    if not isinstance(value, six.string_types):
        raise ValueError('Item "{value!r}" is not a string.'.format(value=value))

    return _unquote(value)


def _validate_hex(value):
    value = _validate_label_text(value)

    if not value.startswith("#"):
        raise ValueError('String "{value}" is not a HEX string. e.g. "#111111".'.format(value=value))

    return value


def _validate_non_zero(value):
    if not isinstance(value, int):
        raise ValueError('Item "{value}" is not an integer!'.format(value=value))

    if value != 0:
        return value

    raise ValueError('Value "{value}" cannot be 0.'.format(value=value))


HEX = _validate_hex
LABEL_TEXT = _validate_label_text
NON_ZERO = _validate_non_zero
STYLE = _validate_comma_separated_list
