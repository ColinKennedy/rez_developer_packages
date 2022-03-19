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
