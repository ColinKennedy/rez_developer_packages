#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""A main module that's responsible for modifying Rez package.py files."""

import parso
from parso import tree

from .adapters import help_adapter, requires_adapter, tests_adapter

_ADAPTERS = {
    "help": help_adapter.HelpAdapter,
    "requires": requires_adapter.RequiresAdapter,
    "tests": tests_adapter.TestsAdapter,
}


def _validate(attribute, data, code):
    """Check if `data` is right for `attribute`.

    Args:
        attribute (str): A Rez attribute to check for issues.
        data (object): Some object(s) to apply to `attribute`.
        code (str): The Rez package.py source code that will be parsed.

    Raises:
        ValueError:
            This function assume that there is something to add so
            `data` cannot be empty. Also, if a given Rez `attribute` is
            not supported or invalid, this function raises ValueError.

    Returns:
        tuple[:class:`parso.python.tree.Module`, :class:`.BaseAdapter`]:
            The parsed `code` and an object that can be used to process it.

    """
    if not data:
        raise ValueError(
            'Data "{data}" cannot be empty. Attribute "{attribute}" will not be modified.'
            "".format(data=data, attribute=attribute)
        )

    try:
        adapter_class = _ADAPTERS[attribute]
    except KeyError:  # pragma: no cover
        raise ValueError(
            'Attribute "{attribute}" is not supported. Options were "{_ADAPTERS}".'
            "".format(attribute=attribute, _ADAPTERS=sorted(_ADAPTERS))
        )

    if not isinstance(data, tree.BaseNode):
        reason_why_invalid = adapter_class.check_if_invalid(data)

        if reason_why_invalid:
            raise ValueError(
                'Data "{data}" is invalid. Reason "{reason_why_invalid}".'.format(
                    data=data, reason_why_invalid=reason_why_invalid
                )
            )

    return parso.parse(code), adapter_class


def add_to_attribute(attribute, data, code, append=False):
    """Add (override) new data onto some Rez package.py attribute.

    Args:
        attribute (str):
            The name of the Rez attribute to modify.
        data (object):
            Anything that you may want to add to `attribute`. If the
            given `attribute` cannot add `data`, ValueError is raised.
        code (str):
            The Rez package.py source code that will be added to.
        append (bool, optional):
            If False, anything in `data` will override the objects
            in `graph` if there are any conflicts between the two.
            If True, the conflicts are ignored and `data` is just
            added to `graph` is if no conflict exists. Default is False.

    Returns:
        str: The modified code that now contains `data` as a part of the given `attribute`.

    """
    graph, adapter_class = _validate(attribute, data, code)

    if adapter_class.supports_duplicates():
        return adapter_class.modify_with_existing(graph, data, append=append)

    return adapter_class.modify_with_existing(graph, data)


def remove_from_attribute(attribute, data, code):
    """From `data` from the `attribute` definition in `code`.

    Args:
        attribute (str):
            The name of the Rez attribute to modify.
        data (object):
            Anything that you may want to remove from `attribute`. If the
            given `attribute` cannot add `data`, ValueError is raised.
        code (str):
            The Rez package.py source code that will be modified.

    Returns:
        str: The modified output of `code`.

    """
    graph, adapter_class = _validate(attribute, data, code)

    return adapter_class.remove_from_attribute(graph, data)
