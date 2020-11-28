#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Assistant functions for traversing and get/set parso nodes."""

def get_node_with_first_prefix(node):
    """Find a node with a prefix attribute.

    If `node` has a prefix, return it. Otherwise, return the first child
    that has one.

    Args:
        node (:class:`parso.python.tree.PythonNode`):
            Some node that may have a prefix attribute or have a child
            that has one.

    Returns:
        :class:`parso.python.tree.PythonNode` or NoneType: The found node, if any.

    """
    if hasattr(node, "prefix"):
        return node

    if not hasattr(node, "children"):
        return None

    for child in iter_nested_children(node):
        if hasattr(child, "prefix"):
            return child

    return None


def iter_nested_children(node):
    """Find every child node of the given `node`, recursively.

    Note:
        This function is **exclusive**, which means `node` is not
        yielded as part of the output. Only its children are yielded.

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
            yield  # pragma: no cover pylint: disable=unreachable

        for child in node.children:
            if child not in seen:
                seen.add(child)

                yield child

                for subchild in _iter_nested_children(child, seen=seen):
                    yield subchild

    for child in _iter_nested_children(node):
        yield child


def iter_parents(node):
    """Find every parent above the given `node`.

    This function is exclusive. It does not yield `node` in its output.

    Args:
        node (:class:`parso.python.tree.PythonNode`): The node to get parents of.

    Yields:
        :class:`parso.python.tree.PythonNode`: The found nodes.

    """
    parent = node.parent

    while parent:
        yield parent

        parent = parent.parent
