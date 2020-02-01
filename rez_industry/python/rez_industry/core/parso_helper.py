#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Functions that make working with :mod:`parso` a little easier."""

from parso.python import tree


# TODO : This was copied from another package. Might be worth making a separate package?
def iter_nested_children(node):
    """Find every child node of the given `node`, recursively.

    Args:
        node (:class:`parso.python.tree.PythonBaseNode`): The node to get children of.

    Yields:
        :class:`parso.python.tree.PythonBaseNode`: The found children.

    """

    def _iter_nested_children(node, seen=None):
        if not seen:
            seen = set()

        if not hasattr(node, "children"):
            return
            yield  # pylint: disable=unreachable

        for child in node.children:
            if child not in seen:
                seen.add(child)

                yield child

                for subchild in _iter_nested_children(child, seen=seen):
                    yield subchild

    for child in _iter_nested_children(node):
        yield child


def find_assignment_nodes(attribute, graph):
    """Get a parso node each time a certain Python attribute is declared and given a value.

    Args:
        attribute (str):
            The name of a Python attribute. e.g. "tests", "help", etc.
        graph (:class:`parso.python.tree.PythonBaseNode`):
            The root node that will be checked. Usually, this is a
            :class:`parso.python.tree.Module` but it doesn't have to be.

    Returns:
        set[:class:`parso.python.tree.PythonBaseNode`]: The found assignments, if any.

    """
    nodes = []

    for child in iter_nested_children(graph):
        if isinstance(child, tree.ExprStmt):
            for name in child.get_defined_names():
                if name.value == attribute:
                    column = name.start_pos[1]

                    if column == 0:
                        nodes.append(child)

    return nodes
