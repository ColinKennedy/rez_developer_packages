#!/usr/bin/env python
# -*- coding: utf-8 -*-


from parso.python import tree

from . import parso_helper


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


def _get_node_with_first_prefix(node):
    if hasattr(node, "prefix"):
        return node

    if not hasattr(node, "children"):
        return None

    for child in parso_helper.iter_nested_children(node):
        if hasattr(child, "prefix"):
            return child

    return None


def _adjust_prefix(nodes, index):
    try:
        marker = nodes[index]
    except IndexError:
        return

    node = _get_node_with_first_prefix(marker)

    if isinstance(node, tree.EndMarker):
        node.prefix = ""
        return

    node.prefix = "\n\n"


def _find_nearest_node_index(nodes, attribute):
    index = _ATTRIBUTES.index(attribute)

    if index == 0:
        raise ValueError('Attribute "{attribute}" cannot be 0.'.format(attribute=attribute))

    output_index = -1
    previous = index - 1

    while previous >= 0 and output_index == -1:
        attribute_to_find = _ATTRIBUTES[previous]

        for index, node in enumerate(nodes):
            if parso_helper.find_assignment_nodes(attribute_to_find, node, inclusive=True):
                output_index = index + 1

        previous -= 1

    return output_index


def _kill_suffix(node):
    for child in reversed(list(parso_helper.iter_nested_children(node))):
        if isinstance(child, tree.Newline):
            child.value = ""

            return


def insert_or_append(node, graph, assignment, attribute):
    if assignment:
        if hasattr(node, "children"):
            node.children[0].prefix = " "

        assignment.children[-1] = node

        return

    index = _find_nearest_node_index(graph.children, attribute)

    if index == -1:
        graph.children.append(
            tree.PythonNode(
                "assignment",
                [tree.String("{attribute} = ".format(attribute=attribute), (0, 0), prefix="\n\n")] + [node],
            )
        )

        return

    _kill_suffix(graph.children[index - 1])

    graph.children.insert(
        index,
        tree.PythonNode(
            "assignment",
            [tree.String("{attribute} = ".format(attribute=attribute), (0, 0), prefix="\n\n")] + [node],
        )
    )
    _adjust_prefix(graph.children, index + 1)
