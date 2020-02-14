#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Functions that make it easier to do basic things in parso."""

from parso.python import tree


def get_replacement_indices(names, parts):
    """Find the start and end indices of some import that need to be changed by `move_break`.

    Args:
        names (iter[:class:`parso.python.tree.Name`]):
            The nodes that represent some Python import namespace.
        parts (iter[str]):
            Some tokens that should match with all or part of `names`,
            in the same order. This parameter is used to figure out if
            any part of `names` will be overwritten by other functions.

    Returns:
        tuple[int, int]:
            The start and end index. If no part of `parts` matches with
            `names`, this function returns (-1, -1).

    """
    names_to_change = []

    for name, old in zip(names, parts):
        if name.value == old:
            names_to_change.append(name)
        else:
            break

    if not names_to_change:
        return [-1, -1]

    # TODO : I think this is copied from elsewhere. Find + make a function for it
    parent = names_to_change[0].parent
    indices = {parent.children.index(name) for name in names_to_change}
    start = min(indices)
    end = max(indices)

    return start, end


def make_replacement_nodes(parts, prefix):
    """Convert namespace tokens into parso nodes.

    Args:
        parts (list[str]):
            The namespace import to convert. e.g. ["foo", "bar", "etc"].
        prefix (str):
            A string that will get placed before the joined result of
            `parts`. Usually, this is just a single " ".

    Returns:
        list[:class:`parso.python.tree.Name` or :class:`parso.python.tree.Operator`]:
            The converted nodes of `parts`.

    """
    new = []

    for index, name in enumerate(parts):
        new.append(tree.Name(name, (0, 0)))

        if index + 1 < len(parts):
            new.append(tree.Operator(".", (0, 0)))

    new[0].prefix = prefix

    return new
