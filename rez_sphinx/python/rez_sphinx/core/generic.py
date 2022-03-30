"""Functions that don't have a logical placement."""


def is_iterable(value):
    """Check if ``value`` is some kind of iterable container.

    Args:
        value (object): Any Python object.

    Returns:
        bool: If iterable, return True.

    """
    try:
        iter(value)
    except TypeError:
        return False

    return True


def decode(text):  # noqa: D403
    """str or unicode: Convert ``text``, if necessary."""
    try:
        return text.decode("utf-8")
    except AttributeError:
        # Python 3 doesn't have `str.decode`
        return text
