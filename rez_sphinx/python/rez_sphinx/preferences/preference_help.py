"""A module to determine how new Rez help entries may be added to :ref:`package help`.

Attributes:
    OPTIONS (dict[str, callable[list[str], str] -> int or str or tuple]):
        A special function for sorting and a string key to refer to it.
        See :func:`validate_order` for details.

"""

import schema

from . import preference_help_


DEFAULT = schema.Use(preference_help_.alphabetical)
OPTIONS = {
    "alphabetical": preference_help_.alphabetical,
    "prefer_generated": preference_help_.prefer_generated,
    "prefer_original": preference_help_.prefer_original,
}


def validate_order(item):
    """Check if ``item`` is a viable sort type.

    Args:
        item (str): A sort option. e.g. "alphabetical".

    Raises:
        ValueError: If ``item`` is not a valid option.

    Returns:
        callable[list[str], str] -> int or str or tuple:
            A function which takes a list of "user preferred" :ref:`package
            help` values, the current value to consider for sorting, and
            returns some kind of sort category.

    """
    try:
        return OPTIONS[item]
    except KeyError:
        raise ValueError(
            'Item "{item}" is invalid. Options were. "{options}".'.format(
                item=item, options=sorted(OPTIONS.keys())
            )
        )
