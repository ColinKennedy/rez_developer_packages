#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The main class used to modify a Rez package's `help` attribute."""

import collections
import copy
import json

import parso
from parso.python import tree
from parso_helper import node_seek
from rez import package_serialise
from rez.vendor.schema import schema

from .. import convention, encoder, parso_utility
from . import base

DEFAULT_HELP_LABEL = "Home Page"


class HelpAdapter(base.BaseAdapter):
    """A class that modifies a Rez package definition `help` attribute.

    In Rez, the "help" attribute can be a "list of list of strings" or
    just a single string. Because the standard varies a bit, a lot of
    logic had to be written to reason through these 2 scenarios.

    """

    @staticmethod
    def _get_entries(assignment):
        """Find every help key + value entry from some "help" attribute.

        If `assignment` is invalid, this function may return an empty list.

        Args:
            assignment (:class:`parso.python.tree.ExprStmt`):
                The node that assigns the "help" attribute, which will
                be modified.

        Returns:
            list[:class:`parso.python.tree.PythonNode`]:
                The list node that is a parso "list of list of strs".

        """
        root = _get_list_root(assignment)

        if root:
            return _get_inner_list_entries(root)

        string_root = _get_str_root(assignment)

        if not string_root:
            return []

        if string_root.get_code().strip() in ("''", '""'):
            return []

        node = tree.PythonNode(
            "testlist_comp",
            [
                tree.String(
                    '"{DEFAULT_HELP_LABEL}"'.format(
                        DEFAULT_HELP_LABEL=DEFAULT_HELP_LABEL
                    ),
                    (0, 0),
                ),
                tree.Operator(",", (0, 0)),
                string_root,
            ],
        )

        for child in node.children:
            child.parent = node

        return [node]

    @staticmethod
    def _resolve_entries(first, second):
        """Figure out what to do with similar help key (label) / value entries.

        The logic goes like this

        - If a label exists in `first` and `second` the one from `first` is removed.
        - Otherwise, the output will always be in order of `first` plus `second`.

        Args:
            first (:class:`parso.python.tree.PythonNode`):
                The inner entry node that should contain only 2
                elements, usually 2 strings. The first string is a
                "label" and the second is a URL or file-path on disk
                that the label points to.
            second (:class:`parso.python.tree.PythonNode`):
                The inner entry node that should contain only 2
                elements, usually 2 strings. The first string is a
                "label" and the second is a URL or file-path on disk
                that the label points to.

        Returns:
            list[:class:`parso.python.tree.PythonNode`]: The resolved label / value entries.

        """
        help_keys = collections.OrderedDict(
            [(node.children[0].get_code(), node.children[0]) for node in first]
        )

        for node in second:
            key = node.children[0]
            code = key.get_code()

            if code in help_keys:
                del help_keys[code]

        output = []

        for value in help_keys.values():
            output.append(value.parent)

        output.extend(second)

        return output

    @staticmethod
    def supports_duplicates():
        """bool: Allow appending duplicate data in :meth:`HelpAdapter.modify_with_existing`."""
        return True

    @staticmethod
    def check_if_invalid(data):
        """str: If `data` is not a str or list-of-lists, return a message."""
        try:
            package_serialise.package_serialise_schema.validate(
                {
                    "name": "",  # This key is required so we just give it nothing
                    "help": data,
                }
            )
        except schema.SchemaError as error:
            return str(error)

        return ""

    @classmethod
    def modify_with_existing(  # pylint: disable=arguments-differ
        cls, graph, data, append=False
    ):
        """Add `data` to a parso node `graph`.

        Reference:
            https://github.com/nerdvegas/rez/wiki/Package-Definition-Guide#help

        Args:
            graph (:class:`parso.python.Tree.PythonBaseNode`):
                Some node that may assignment an attribute called
                "tests". If "tests" assignment exists, it gets
                overwritten. If no assignment exists then a new
                assignment is appended to the end of the file.
            data (list[list[str]] or str or :class:`parso.python.tree.PythonNode`):
                Any values that'd typically define a Rez "tests"
                attribute. Basically anything is allowed, as long the
                Rez package schema considers it valid.
            append (bool, optional):
                If False, anything in `data` will override the objects
                in `graph` if there are any conflicts between the two.
                If True, the conflicts are ignored and `data` is just
                added to `graph` is if no conflict exists. Default is False.

        Returns:
            str:
                The modified Python source code. It should resemble the
                source code of `graph` plus any serialized `data`.

        """
        assignments = parso_utility.find_assignment_nodes("help", graph) or parso_utility.find_definition_root_nodes("help", graph)

        try:
            assignment = assignments[-1]
        except IndexError:
            assignment = None

        if isinstance(data, tree.BaseNode):
            graph = convention.insert_or_append_raw_node(
                data, graph, assignment, "help"
            )

            return graph.get_code()

        help_data = parso.parse(json.dumps(data, cls=encoder.BuiltinEncoder)).children[
            0
        ]

        if (
            assignment
            and not _get_list_root(assignment)
            and isinstance(help_data, tree.String)
        ):
            help_data.prefix = " "
            graph = convention.insert_or_append(help_data, graph, assignment, "help")

            return graph.get_code()

        if _get_list_root(assignment) and isinstance(help_data, tree.String):
            raise ValueError(
                'You may not add string "{help_data}" '
                'because assignment "{assignment}" is a list.'.format(
                    help_data=help_data.get_code(), assignment=assignment.get_code()
                )
            )

        help_data = _get_inner_list_entries(help_data)

        entries = []

        if assignment:
            entries = cls._get_entries(assignment)

        if not append:
            entries = cls._resolve_entries(entries, help_data)
        else:
            entries.extend(help_data)

        entries = [
            tree.PythonNode(
                "atom", [tree.Operator("[", (0, 0)), entry, tree.Operator("]", (0, 0))]
            )
            for entry in entries
        ]
        entries = _separate_with_commas(entries)

        node = tree.PythonNode(
            "atom",
            [tree.Operator("[", (0, 0))]
            + entries
            + [tree.Operator(",", (0, 0)), tree.Operator("]", (0, 0))],
        )

        node = _apply_formatting(node)

        graph = convention.insert_or_append(node, graph, assignment, "help")

        return graph.get_code()

    @staticmethod
    def remove_from_attribute(graph, data):
        """Delete `data` from `graph`, if it exists.

        Args:
            graph (:class:`parso.python.tree.Module`):
                The parso node that will contains a "help" attribute
                that this function will modify.
            data (list[list[str]] or str):
                Any values that'd typically define a Rez "tests"
                attribute. Basically anything is allowed, as long the
                Rez package schema considers it valid.

        Returns:
            str: The original `graph` but as a result of the deleted content.

        """
        raise NotImplementedError("This feature hasn't been added.")


def _is_list_root_definition(node):
    """bool: If `node` defines the inner part of a list of "help" entries."""
    return isinstance(node, tree.PythonNode) and node.type == "testlist_comp"


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


def _get_list_root(node):
    """Find the first node that could be considered the root of a "help" attribute.

    Args:
        node (:class:`parso.python.tree.ExprStmt`):
            A node that defines a "help" attribute and should contain a
            list of list of strings.

    Returns:
        :class:`parso.python.tree.PythonNode` or NoneType:
            The top of a list of list of strings, if any.

    """
    for child in node_seek.iter_nested_children(node):
        if _is_list_root_definition(child):
            return child

    return None


def _get_str_root(node):
    """Find the first node that could be considered the root of a "help" attribute.

    Args:
        node (:class:`parso.python.tree.ExprStmt`):
            A node that defines a "help" attribute and should contain a
            string help URL or file path.

    Returns:
        :class:`parso.python.tree.PythonNode` or NoneType:
            The URL / file-path node, if any.

    """
    for child in node_seek.iter_nested_children(node):
        if isinstance(child, tree.String):
            return child

    return None


def _apply_formatting(node):
    """Get a copy of `node` that has "human-readable" whitespace.

    Args:
        node (:class:`parso.python.Tree.PythonBaseNode`):
            A parso object that represents the top-level "list of list
            of strings" that defines a Rez help attribute.

    Returns:
        :class:`parso.python.Tree.PythonBaseNode`: The copy of `node` that has nice newlines.

    """

    def _needs_space(node):
        if isinstance(node, tree.Operator) and node.value in ("[", "]"):
            return False

        if isinstance(node, tree.String):
            return False

        return True  # pragma: no cover

    def _iter_inner_entries(node):
        for child in node_seek.iter_nested_children(node):
            if isinstance(child, tree.PythonNode) and child.type == "atom":
                yield child

    node = copy.deepcopy(node)

    for child in node_seek.iter_nested_children(node):
        if isinstance(child, tree.Operator) and child.value == ",":
            child.prefix = ""
        elif hasattr(child, "prefix") and _needs_space(child):
            child.prefix = " "  # pragma: no cover

    for child in _iter_inner_entries(node):
        opening_brace = child.children[0]
        opening_brace.prefix = "\n    "

    node.children[-1].prefix = "\n"

    return node


def _separate_with_commas(nodes):
    """Add a comma between every parso node, starting at the first element.

    Args:
        nodes (list): Some objects that will get parso nodes inserted between its elements.

    Returns:
        list[:class:`parso.python.Tree.PythonBaseNode`]:
            The original `nodes` plus comma operators.

    """
    nodes = copy.deepcopy(nodes)

    for index in reversed(range(1, len(nodes))):
        nodes.insert(index, tree.Operator(",", (0, 0)))

    return nodes
