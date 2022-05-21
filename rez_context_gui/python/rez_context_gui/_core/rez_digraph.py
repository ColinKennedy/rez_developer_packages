"""A small module for interacting with :ref:`digraphs <digraph>` from Rez."""

from .schemas import _attribute

_CONFLICT_KEY = "fontcolor"
_CONFLICT_COLOR = "red"
_CONFLICT_VALIDATOR = _attribute.get_from_name(_attribute.FONT_COLOR)


def is_conflict_edge(attributes):
    """Check if the given edge ``attributes`` describes a package conflict.

    Args:
        attributes (iter[str, object]):
            Each digraph edge to check. It contains iterable key / value pairs.

    Returns:
        bool: If there's package conflict, return True.

    """
    for key, value in attributes:
        if key != _CONFLICT_KEY:
            continue

        if _CONFLICT_VALIDATOR(value) == _CONFLICT_COLOR:
            return True

    return False
