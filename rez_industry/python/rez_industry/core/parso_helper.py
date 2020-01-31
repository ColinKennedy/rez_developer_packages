#!/usr/bin/env python
# -*- coding: utf-8 -*-

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
    nodes = []

    for child in iter_nested_children(graph):
        if isinstance(child, tree.ExprStmt):
            for name in child.get_defined_names():
                if name.value == attribute:
                    column = name.start_pos[1]

                    if column == 0:
                        nodes.append(child)

    return nodes


