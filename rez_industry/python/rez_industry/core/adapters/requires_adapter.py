#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The main class used to modify a Rez package's `requires` attribute."""

import collections
import copy
import json

import parso
from parso.python import tree
from parso_helper import node_seek
from rez.vendor.version import requirement as rez_requirement
from rez import package_serialise
from rez.vendor.schema import schema

from .. import convention, parso_utility
from . import base

_DEFAULT_PREFIX = "    "


class RequiresAdapter(base.BaseAdapter):
    """The main class used to modify a Rez package's `requires` attribute."""

    @staticmethod
    def check_if_invalid(data):
        """str: If `data` is invalid, return a message explaining why."""
        try:
            package_serialise.package_serialise_schema.validate(
                {
                    "name": "",  # This key is required so we just give it nothing
                    "requires": data,
                }
            )
        except schema.SchemaError as error:
            return str(error)

        return ""

    @staticmethod
    def modify_with_existing(graph, data):
        # """Add `data` to a parso node `graph`.
        #
        # Args:
        #     graph (:class:`parso.python.Tree.PythonBaseNode`):
        #         Some node that will either be appended to or have some
        #         of its contents overwritten and returned.
        #     data (object):
        #         Whatever data will be added to `graph`. It's up to
        #         subclasses to figure out what kind of data is needed and
        #         how it will be added.
        #
        # Returns:
        #     str:
        #         The modified Python source code. It should resemble the
        #         source code of `graph` plus any serialized `data`.
        #
        # """
        try:
            assignment = parso_utility.find_assignment_nodes("requires", graph)[-1]
        except IndexError:
            assignment = None

        existing_data = _get_entries(assignment)
        prefix = _get_prefix(assignment) or _DEFAULT_PREFIX

        data_nodes = [
            tree.String(
                '"{requirement}"'.format(
                    requirement=requirement.replace('"', '"')
                ),
                (0, 0),
                prefix="\n{prefix}".format(prefix=prefix),
            )
            for requirement in data
        ]

        final_data = _merge_list_entries(existing_data, data_nodes)
        node = _make_new_list(final_data)
        graph = convention.insert_or_append(node, graph, assignment, "requires")

        return graph.get_code()


def _get_entries(node):
    root_entries = _get_inner_list_entries(node)

    if not root_entries:
        return []

    entries = []

    for item in root_entries:
        for child in node_seek.iter_nested_children(item):
            if not isinstance(child, tree.Operator):
                entries.append(child)

    return entries


def _get_prefix(node):
    prefixes = set()

    for child in _get_inner_list_entries(node):
        prefix_node = node_seek.get_node_with_first_prefix(child)
        prefixes.add(prefix_node.prefix)

    counter = collections.Counter(prefixes)

    try:
        common = counter.most_common(1)[0]

        return common[0].strip("\n")
    except IndexError:
        return ""


# TODO : De-duplicate this
def _get_inner_list_entries(node):
    """Find the literal "help" entries of a node.

    Args:
        node (:class:`parso.python.tree.PythonBaseNode`):
            A parso object that (we assume) has 0+ child list parso
            objects. Each child found is returned.

    Returns:
        list[:class:`parso.python.tree.PythonNode`]:
            The found key / value "help" attribute entries, if any.

    """
    entries = []

    for child in node_seek.iter_nested_children(node):
        if not _is_list_root_definition(child):
            continue

        if any(
            child_ for child_ in child.children if isinstance(child_, tree.PythonNode)
        ):
            continue

        entries.append(child)

    return entries


def _is_list_root_definition(node):
    """bool: If `node` defines the inner part of a list of "help" entries."""
    return isinstance(node, tree.PythonNode) and node.type == "testlist_comp"


# def _get_list_root(node):
#     """Find the first node that could be considered the root of a "help" attribute.
#
#     Args:
#         node (:class:`parso.python.tree.ExprStmt`):
#             A node that defines a "help" attribute and should contain a
#             list of list of strings.
#
#     Returns:
#         :class:`parso.python.tree.PythonNode` or NoneType:
#             The top of a list of list of strings, if any.
#
#     """
#     for child in node_seek.iter_nested_children(node):
#         if _is_list_root_definition(child):
#             return child
#
#     return None


def _escape(text):
    return text.strip('"')


def _make_new_list(requirements):
    nodes = []

    for requirement in requirements:
        nodes.append(requirement)
        nodes.append(tree.Operator(",", (0, 0)))

    prefix = "\n"

    if not nodes:
        prefix = ""

    return tree.PythonNode(
        "atom",
        [tree.Operator("[", (0, 0))] + nodes + [tree.Operator("]", (0, 0), prefix=prefix)],
    )


def _merge_list_entries(old, new):
    def _find_index(nodes, text):
        for index, node in enumerate(nodes):
            requirement = _escape(node.value)
            requirement = rez_requirement.Requirement(requirement)

            if requirement.name > text:
                return index

        return len(nodes)

    def _remove_existing_entries(old, new):
        # Since `requires` doesn't really play nice with duplicate entries,
        # we will remove any existing requirements that match any entries in `new`.
        #
        for entry in reversed(new):
            new_requirement = rez_requirement.Requirement(_escape(entry.value))
            package_family = new_requirement.name

            for requirement in reversed(old):
                old_requirement = rez_requirement.Requirement(_escape(requirement.value))

                if old_requirement.name == package_family:
                    parent = requirement.parent
                    index = old.index(requirement)

                    del old[index]

    old = copy.deepcopy(old)

    _remove_existing_entries(old, new)

    for entry in new:
        requirement = rez_requirement.Requirement(_escape(entry.value))
        index = _find_index(old, requirement.name)
        old.insert(index, entry)

    return old
