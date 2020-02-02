#!/usr/bin/env python
# -*- coding: utf-8 -*-

import copy
import collections
import json

import parso
import six
from parso.python import tree
from rez import package_serialise
from rez.vendor.schema import schema

from .. import parso_helper
from . import base

_DEFAULT_FALLBACK_KEY = "documentation"


class HelpAdapter(base.BaseAdapter):
    @staticmethod
    def _get_entries(assignment):
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
                    '"{_DEFAULT_FALLBACK_KEY}"'.format(
                        _DEFAULT_FALLBACK_KEY=_DEFAULT_FALLBACK_KEY,
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
        help_keys = collections.OrderedDict([(node.children[0].get_code(), node.children[0]) for node in first])

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
    def modify_with_existing(cls, graph, data, append=False):
        def _insert_or_append(node, graph, assignment):
            if assignment:
                if hasattr(node, "children"):
                    node.children[0].prefix = " "

                assignment.children[-1] = node
            else:
                graph.children.append(
                    tree.PythonNode(
                        "assignment",
                        [tree.String("help = ", (0, 0), prefix="\n\n")] + [node],
                    )
                )

        try:
            assignment = parso_helper.find_assignment_nodes("help", graph)[-1]
        except IndexError:
            assignment = None

        help_data = parso.parse(json.dumps(data)).children[0]

        if assignment and not _get_list_root(assignment) and isinstance(help_data, tree.String):
            help_data.prefix = " "
            _insert_or_append(help_data, graph, assignment)

            return graph.get_code()

        if _get_list_root(assignment) and isinstance(help_data, tree.String):
            raise ValueError('You may not add string "{help_data}" because assignment "{assignment}" is a list.'.format(
                help_data=help_data.get_code(), assignment=assignment.get_code())
            )

        help_data = _get_inner_list_entries(help_data)

        entries = []

        if assignment:
            entries = cls._get_entries(assignment)

        if not append:
            entries = cls._resolve_entries(entries, help_data)
        else:
            entries.extend(help_data)

        entries = [tree.PythonNode("atom", [tree.Operator("[", (0, 0)), entry, tree.Operator("]", (0, 0))]) for entry in entries]
        entries = _separate_with_commas(entries)

        node = tree.PythonNode(
            "atom",
            [tree.Operator("[", (0, 0))] + entries + [tree.Operator(",", (0, 0)), tree.Operator("]", (0, 0))],
        )

        node = _apply_formatting(node)

        _insert_or_append(node, graph, assignment)

        return graph.get_code()


def _is_list_root_definition(node):
    return isinstance(node, tree.PythonNode) and node.type == "testlist_comp"


def _get_inner_list_entries(node):
    entries = []

    for child in parso_helper.iter_nested_children(node):
        if not _is_list_root_definition(child):
            continue

        if any(child_ for child_ in child.children if isinstance(child_, tree.PythonNode)):
            continue

        entries.append(child)

    return entries


def _get_list_root(node):
    for child in parso_helper.iter_nested_children(node):
        if _is_list_root_definition(child):
            return child

    return None


def _get_str_root(node):
    for child in parso_helper.iter_nested_children(node):
        if isinstance(child, tree.String):
            return child

    return None


def _apply_formatting(node):
    def _needs_space(node):
        if isinstance(node, tree.Operator) and node.value in ("[", "]"):
            return False

        if isinstance(node, tree.String):
            return False

        return True  # pragma: no cover

    def _iter_inner_entries(node):
        for child in parso_helper.iter_nested_children(node):
            if isinstance(child, tree.PythonNode) and child.type == "atom":
                yield child

    node = copy.deepcopy(node)

    for child in parso_helper.iter_nested_children(node):
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
    nodes = copy.deepcopy(nodes)

    # Add a comma between every element, starting at the first element
    for index in reversed(range(1, len(nodes))):
        nodes.insert(index, tree.Operator(",", (0, 0)))

    return nodes
