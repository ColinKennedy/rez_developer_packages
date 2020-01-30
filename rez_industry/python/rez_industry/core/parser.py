#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""A main module that's responsible for modifying Rez package.py files."""

import os

import parso
from rez import packages_

from . import parser_adapter

_ADAPTERS = {
    "help": parser_adapter.HelpAdapter,
    "tests": parser_adapter.TestsAdapter,
}


def add_to_attribute(attribute, data, code):
    """Add (override) new data onto some Rez package.py attribute.

    Args:
        attribute (str):
            The name of the Rez attribute to modify.
        data (object):
            Anything that you may want to add to `attribute`. If the
            given `attribute` cannot add `data`, ValueError is raised.
        code (str):
            The Rez package.py source code that will be added to.

    Raises:
        ValueError:
            This function assume that there is something to add so
            `data` cannot be empty. Also, if a given Rez `attribute` is
            not supported or invalid, this function raises ValueError.

    Returns:
        str: The modified code that now contains `data` as a part of the given `attribute`.

    """
    if not data:
        raise ValueError('Object "{data}" cannot be empty.'.format(data=data))

    try:
        adapter_class = _ADAPTERS[attribute]
    except KeyError:
        raise ValueError(
            'Attribute "{attribute}" is not supported. Options were "{_ADAPTERS}".'
            "".format(attribute=attribute, _ADAPTERS=sorted(_ADAPTERS))
        )

    reason_why_invalid = adapter_class.check_if_invalid(data)

    if reason_why_invalid:
        raise ValueError(
            'Data "{data}" is invalid. Reason "{reason_why_invalid}".'.format(
                data=data, reason_why_invalid=reason_why_invalid
            )
        )

    graph = parso.parse(code)

    return adapter_class.modify_with_existing(graph, data)
