"""A companion module for :mod:`preference_help`."""


def alphabetical(_, item):
    """Sort ``item`` in ascending, alphabetical order.

    Args:
        item (list[str, str]): Some `package help`_ entry to consider for sorting.

    Returns:
        str: The original ``item``.

    """
    return item


def filter_generated(original_help, generated_help):
    """Remove any entry in ``original_help`` which conflicts with ``generated_help``.

    Args:
        original_help (list[list[str, str]):
            The `package help`_ which came directly from the user's Rez
            `package.py`_.
        generated_help (list[list[str, str]):
            The `package help`_ which :ref:`rez_sphinx` created, based on
            the content in the user's source Rez package.

    Returns:
        list[list[str, str], list[str, str]]:
            The filtered `package help`_ and the original, unedited
            auto-generated `package help`_.

    """
    labels = {label for label, _ in original_help}

    output = [
        [label, destination]
        for label, destination in generated_help
        if label not in labels
    ]

    return original_help, output


def filter_none(original_help, generated_help):
    """Don't filter anything, from either list.

    Args:
        original_help (list[list[str, str]):
            The `package help`_ which came directly from the user's Rez
            `package.py`_.
        generated_help (list[list[str, str]):
            The `package help`_ which :ref:`rez_sphinx` created, based on
            the content in the user's source Rez package.

    Returns:
        list[list[str, str], list[str, str]]: Both lists, unedited.

    """
    return original_help, generated_help


def filter_original(original_help, generated_help):
    """Remove any entry in ``generated_help`` which conflicts with ``original_help``.

    Args:
        original_help (list[list[str, str]):
            The `package help`_ which came directly from the user's Rez
            `package.py`_.
        generated_help (list[list[str, str]):
            The `package help`_ which :ref:`rez_sphinx` created, based on
            the content in the user's source Rez package.

    Returns:
        list[list[str, str], list[str, str]]:
            The original, unedited `package help`_ and the filtered
            auto-generated `package help`_.

    """
    labels = {label for label, _ in generated_help}

    output = [
        [label, destination]
        for label, destination in original_help
        if label not in labels
    ]

    return output, generated_help


def sort_generated(original_help, item):
    """Sort auto-generated ``item`` before anything in ``original_help``.

    Args:
        original_help (list[list[str, str]]):
            All `package help`_ entries which the user already defined on
            their `package.py`_ prior to running this sort function.
        item (list[str, str]):
            Some `package help`_ entry to consider for sorting.

    Returns:
        tuple[int, int or str]: The group index, followed by a secondary sort term.

    """
    try:
        return (1, original_help.index(item))
    except ValueError:
        return (0, item)


def sort_original(original_help, item):
    """Sort hand-written from ``original_help`` before sorting ``item``.

    Args:
        original_help (list[list[str, str]]):
            All `package help`_ entries which the user already defined on
            their `package.py`_ prior to running this sort function.
        item (list[str, str]):
            Some `package help`_ entry to consider for sorting.

    Returns:
        tuple[int, int or str]: The group index, followed by a secondary sort term.

    """
    try:
        return (0, original_help.index(item))
    except ValueError:
        return (1, item)
