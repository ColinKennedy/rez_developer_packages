#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""A series of "non-essential and totally arbitrary" rules for inserting Rez attributes.

Basically, if an attribute doesn't exist in a Rez package, instead of
adding it to the end or beginning of the package.py, this module tries
its best to put it somewhere in the middle, if it can.

"""

from parso.python import tree
from parso_helper import node_seek

from . import parso_utility

_ATTRIBUTES = (
    "name",
    "version",
    "description",
    "authors",
    "help",
    "requires",
    "tests",
    "private_build_requires",
    "build_requires",
    "commands",
)


def _adjust_prefix(nodes, index):
    """Remove whitespace information or add it, if needed.

    This function should be applied directly to whatever node lies
    **after** the Rez attribute that was inserted.

    The logic goes like this.

    - If the index after the inserted attribute doesn't have an
      EndMarker then that means the attribute was inserted at the end of the
      parso graph
      - This means the attribute is at the end of the parsed graph.
      - Because it's at the end, we don't need any newlines.
    - If the index does exist but it's at the end of the graph, same
      thing. We don't need newlines.
    - If there's a node after `index` and it's not an EndMarker then that means
      the inserted attribute was inserted between two parso nodes. Which
      means it's in the middle of the file.
      - Add 2 newlines

    Args:
        nodes (iter[:class:`parso.python.tree.PythonNode`]): The direct children
            of a Rez package.py which had some attribute inserted.
        index (int): The 0-based position where the attribute was inserted.

    """
    try:
        marker = nodes[index + 1]
    except IndexError:
        return

    node = node_seek.get_node_with_first_prefix(marker)

    if isinstance(node, tree.EndMarker):
        node.prefix = ""

        return

    if hasattr(node, "prefix"):
        node.prefix = "\n\n"


def _append_or_insert_node(node, graph, assignment, attribute):
    if assignment:
        index = _find_nearest_node_index(graph.children, attribute)
        del graph.children[index]
        graph.children.insert(index, tree.PythonNode("assignment", [node]))

        return graph

    index = _find_nearest_node_index(graph.children, attribute)

    if index == -1:
        graph.children.append(tree.PythonNode("assignment", [node]))

        return graph

    prefix_node = node_seek.get_node_with_first_prefix(node)
    prefix_node.prefix = "\n\n"
    graph.children.insert(index, tree.PythonNode("assignment", [node]))

    return graph


def _find_nearest_node_index(nodes, attribute):
    """Get the position used to insert `attribute` into the final Rez package.py file.

    Args:
        nodes (iter[:class:`parso.python.tree.PythonNode`]):
            The direct children of a Rez package.py which will be
            used to search for the right index for `attribute` to be inserted.
        attribute (str):
            The name of the Rez-related object to use.

    Raises:
        ValueError: If `attribute` is not a valid Rez attribute.

    Returns:
        int: A positive, non-zero number that will be used to insert an attribute later.

    """
    index = _ATTRIBUTES.index(attribute)

    if index == 0:
        raise ValueError(
            'Attribute "{attribute}" cannot be 0.'.format(attribute=attribute)
        )

    output_index = -1
    previous = index - 1

    while previous >= 0 and output_index == -1:
        attribute_to_find = _ATTRIBUTES[previous]

        for index, node in enumerate(nodes):
            if parso_utility.find_assignment_nodes(
                attribute_to_find, node, inclusive=True
            ):
                output_index = index + 1

        previous -= 1

    return output_index


def _kill_suffix(node):
    """Remove any trailing newlines from `node`."""
    for child in reversed(list(node_seek.iter_nested_children(node))):
        if isinstance(child, tree.Newline):
            child.value = ""

            return


def insert_or_append(node, graph, assignment, attribute):
    """Add a new `attribute` to `graph`, according to pre-existing data.

    Args:
        node (:class:`parso.python.tree.PythonNode`):
            The main data that will be added to `graph`.
        graph (:class:`parso.python.tree.PythonNode`):
            A Python module that may already contain an assignment for
            `attribute`. If it doesn't the attribute will be added,
            automatically.
        assignment (:class:`parso.python.tree.PythonNode` or NoneType):
            If `graph` has an existing node where `attribute` is
            defined, this node will represent that position. If this
            parameter is None, a new position for `attribute` will be
            automatically found and used.
        attribute (str):
            The name of the Rez-related object to use.

    Returns:
        :class:`parso.python.tree.PythonNode`: The main module with a modified `attribute`.

    """
    if isinstance(node, tree.BaseNode):
        return _append_or_insert_node(node, graph, assignment, attribute)

    if assignment:
        if hasattr(node, "children"):
            node.children[0].prefix = " "

        assignment.children[-1] = node

        return graph

    index = _find_nearest_node_index(graph.children, attribute)

    if index == -1:
        graph.children.append(
            tree.PythonNode(
                "assignment",
                [
                    tree.String(
                        "{attribute} = ".format(attribute=attribute),
                        (0, 0),
                        prefix="\n\n",
                    )
                ]
                + [node],
            )
        )

        return graph

    _kill_suffix(graph.children[index - 1])

    graph.children.insert(
        index,
        tree.PythonNode(
            "assignment",
            [
                tree.String(
                    "{attribute} = ".format(attribute=attribute), (0, 0), prefix="\n\n"
                )
            ]
            + [node],
        ),
    )
    _adjust_prefix(graph.children, index)

    return graph
