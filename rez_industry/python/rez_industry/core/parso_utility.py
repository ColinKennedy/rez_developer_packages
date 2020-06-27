#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Functions that make working with :mod:`parso` a little easier."""

import itertools

from parso.python import tree
from parso_helper import node_seek


def find_assignment_nodes(attribute, graph, inclusive=False):
    """Get a parso node each time a certain Python attribute is declared and given a value.

    Args:
        attribute (str):
            The name of a Python attribute. e.g. "tests", "help", etc.
        graph (:class:`parso.python.tree.PythonBaseNode`):
            The root node that will be checked. Usually, this is a
            :class:`parso.python.tree.Module` but it doesn't have to be.
        inclusive (bool, optional):
            If True, include `graph` as the first item to be iterated
            over. If False, only iterate over `graph`'s children,
            recursively. Default is False.

    Returns:
        set[:class:`parso.python.tree.PythonBaseNode`]: The found assignments, if any.

    """
    nodes = []

    items = node_seek.iter_nested_children(graph)

    if inclusive:
        items = itertools.chain([graph], items)

    for child in items:
        if isinstance(child, tree.ExprStmt):
            for name in child.get_defined_names():
                if name.value == attribute:
                    column = name.start_pos[1]

                    if column == 0:
                        nodes.append(child)

    return nodes


def find_def_nodes(attribute, nodes):
    """Get a parso node each time a certain Python function is declared and given a value.

    Args:
        attribute (str):
            The name of a Python attribute. e.g. "tests", "help", etc.
        nodes (iter[:class:`parso.python.tree.PythonBaseNode`]):
            Every node to check for definitions. For a Rez package.py,
            this is normally the parso root node's children. e.g.
            `node.get_root_node().children`.

    Returns:
        set[:class:`parso.python.tree.PythonBaseNode`]: The found definitions, if any.

    """
    output = set()

    for node in nodes:
        if not isinstance(node, tree.Function):
            continue

        if node.name == attribute:
            output.add(node)

    return output
