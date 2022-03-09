"""A companion module for :mod:`preference_help`."""


def alphabetical(_, item):
    """Sort ``item`` in ascending, alphabetical order.

    Args:
        item (list[str, str]): Some :ref:`package help` entry to consider for sorting.

    Returns:
        str: The original ``item``.

    """
    return item


def prefer_generated(original_help, item):
    """Sort auto-generated ``item`` before anything in ``original_help``.

    Args:
        original_help (list[list[str, str]]):
            All :ref:`package help` entries which the user already defined on
            their :ref:`package.py` prior to running this sort function.
        item (list[str, str]):
            Some :ref:`package help` entry to consider for sorting.

    Returns:
        tuple[int, int or str]: The group index, followed by a secondary sort term.

    """
    try:
        return (1, original_help.index(item))
    except ValueError:
        return (0, item)


def prefer_original(original_help, item):
    """Sort hand-written from ``original_help`` before sorting ``item``.

    Args:
        original_help (list[list[str, str]]):
            All :ref:`package help` entries which the user already defined on
            their :ref:`package.py` prior to running this sort function.
        item (list[str, str]):
            Some :ref:`package help` entry to consider for sorting.

    Returns:
        tuple[int, int or str]: The group index, followed by a secondary sort term.

    """
    try:
        return (0, original_help.index(item))
    except ValueError:
        return (1, item)
