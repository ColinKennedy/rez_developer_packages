"""A module to determine how new Rez help entries may be added to `package help`_.

Attributes:
    OPTIONS (dict[str, callable[list[str], str] -> int or str or tuple]):
        A special function for sorting and a string key to refer to it.
        See :func:`validate_sort` for details.

"""

import schema

from . import preference_help_

DEFAULT_FILTER = schema.Use(preference_help_.filter_generated)
DEFAULT_SORT = schema.Use(preference_help_.alphabetical)
OPTIONS = {
    "alphabetical": preference_help_.alphabetical,
    "prefer_generated": preference_help_.sort_generated,
    "prefer_original": preference_help_.sort_original,
}
_FILTERERS = {
    "none": preference_help_.filter_none,
    "prefer_generated": preference_help_.filter_original,
    "prefer_original": preference_help_.filter_generated,
}


def validate_filter(item):
    """Check if ``item`` is a viable filter type.

    Args:
        item (str): A sort option. e.g. "prefer_original".

    Raises:
        ValueError: If ``item`` is not a valid option.

    Returns:
        callable[
            list[list[str, str]],
            list[list[str, str]]
        ] -> tuple[
            list[list[str, str]],
            list[list[str, str]]
        ]:
            A function that takes two `package help`_ lists and may return
            unique results from either of them.

    """
    try:
        return _FILTERERS[item]
    except KeyError:
        raise ValueError(
            'Item "{item}" is invalid. Options were. "{options}".'.format(
                item=item, options=sorted(OPTIONS.keys())
            )
        )


def validate_sort(item):
    """Check if ``item`` is a viable sort type.

    Args:
        item (str): A sort option. e.g. "alphabetical".

    Raises:
        ValueError: If ``item`` is not a valid option.

    Returns:
        callable[list[str], str] -> int or str or tuple:
            A function which takes a list of "user preferred" `package help`_
            values, the current value to consider for sorting, and returns some
            kind of sort category.

    """
    try:
        return OPTIONS[item]
    except KeyError:
        raise ValueError(
            'Item "{item}" is invalid. Options were. "{options}".'.format(
                item=item, options=sorted(OPTIONS.keys())
            )
        )
