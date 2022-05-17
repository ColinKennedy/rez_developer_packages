"""A series of schemas for validating / transforming raw text and objects.

When Rez converts a :ref:`context` into a :ref:`digraph`, some of the digraph
settings are a bit too primitive. Like instead of storing a list of strings, it
makes a CSV string like ``"foo,bar,fizz,buzz"``. This module is for making sure
those values are correct and transforming them into more useful Python objects.

"""

import six

_COMMA_SEPARATOR = ","
_QUOTES = ('"', "'")


def _unquote(text):
    """Remove any leading / trailing " / ' character from ``text``.

    Args:
        text (str): Some string to strip, like ``'"foo"'``.

    Returns:
        str: The stripped text, e.g. ``"foo"``.

    """
    if text.startswith(_QUOTES):
        text = text[1:]

    if text.endswith(_QUOTES):
        text = text[:-1]

    return text


def _validate_comma_separated_list(value):
    """Split a CSV ``value`` into a list of strings.

    Args:
        value (object): Some item to verify.

    Returns:
        list[str]: The split values.

    """
    value = _validate_label_text(value)

    output = []

    for item in value.split(_COMMA_SEPARATOR):
        item = item.strip()

        if item:
            output.append(item)

    return output


def _validate_label_text(value):
    """Find and clean a label from ``value``.

    Sometimes, strings have escaped ""s surrounding them. This function strips
    them (since they're pointless).

    Args:
        value (object): Some item to verify.

    Raises:
        ValueError: If ``value`` is not a label.

    Returns:
        str: The ``value`` but without beginning / ending quotes.

    """
    if not isinstance(value, six.string_types):
        raise ValueError('Item "{value!r}" is not a string.'.format(value=value))

    return _unquote(value)


def _validate_hex(value):
    """Ensure ``value`` is a hex color string, like ``"#111111"``.

    Args:
        value (object): Some item to verify.

    Raises:
        ValueError: If ``value`` is not a hex color string.

    Returns:
        str: The original value.

    """
    value = _validate_label_text(value)

    if not value.startswith("#"):
        raise ValueError(
            'String "{value}" is not a HEX string. e.g. "#111111".'.format(value=value)
        )

    return value


def _validate_non_zero(value):
    """Ensure ``value`` is a non-zero integer.

    Args:
        value (object): Some item to verify.

    Raises:
        ValueError: If ``value`` is not an integer or is zero.

    Returns:
        int: The original value.

    """
    if not isinstance(value, int):
        raise ValueError('Item "{value}" is not an integer!'.format(value=value))

    if value != 0:
        return value

    raise ValueError('Value "{value}" cannot be 0.'.format(value=value))


HEX = _validate_hex
LABEL_TEXT = _validate_label_text
NON_ZERO = _validate_non_zero
STYLE = _validate_comma_separated_list
