#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""A module for converting rich, parso-esque objects to built-in types."""

import operator


def to_dot_namespace(names):
    """Combine parso names into a dot-separated namespace.

    Args:
        names (iter[:class:`parso.python.tree.PythonNode`]): The objects to combine.

    Returns:
        str: A dot-separated namespace.

    """
    return ".".join(map(operator.attrgetter("value"), names))
