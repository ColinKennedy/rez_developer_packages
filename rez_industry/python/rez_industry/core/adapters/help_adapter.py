#!/usr/bin/env python
# -*- coding: utf-8 -*-

import copy
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
            return [root]

        string_root = _get_str_root(assignment)

        if not string_root:
            return []

        if string_root.get_code().strip() in ("''", '""'):
            return []

        return [
            tree.PythonNode(
                "atom",
                [
                    tree.Operator("[", (0, 0)),
                    tree.PythonNode(
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
                    ),
                    tree.Operator("]", (0, 0)),
                ],
            ),
        ]

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

        entries = []

        if assignment:
            entries = cls._get_entries(assignment)

        # if not isinstance(entries, tree.String) and isinstance(data, six.string_types):
        #     raise ValueError(
        #         'Data "{data}" is a string. And a help string cannot replace '
        #         'a help list-of-lists.'.format(data=data))
        #
        # if not append and not isinstance(data, six.string_types):
        #     invalids = [item for item in data if item in entries]
        #
        #     if invalids:
        #         raise ValueError(
        #             'Duplicate entries "{invalids}" were found. '
        #             'Re-run with `append=True` or remove the duplicates to contine.'
        #             ''.format(invalids=invalids)
        #         )

        help_data = parso.parse(json.dumps(data)).children[0]
        # ValueError: PythonNode(atom, [<Operator: [>, PythonNode(testlist_comp, [PythonNode(atom, [<Operator: [>, PythonNode(testlist_comp, [<String: "woo">, <Operator: ,>, <String: "blah">]), <Operator: ]>]), <Operator: ,>, PythonNode(atom, [
        # <Operator: [>, PythonNode(testlist_comp, [<String: "thing">, <Operator: ,>, <String: "another">]), <Operator: ]>])]), <Operator: ]>])
        inner_help_entries = help_data.children[1]

        if entries and not _is_comma(entries[-1]) and not _is_comma(entries[-1].children[-1]):
            entries.append(tree.Operator(",", (0, 0)))

        entries.append(inner_help_entries)

        if not _is_comma(entries[-1]):
            entries.append(tree.Operator(",", (0, 0)))

        node = tree.PythonNode(
            "atom",
            [tree.Operator("[", (0, 0))] + entries + [tree.Operator("]", (0, 0))],
        )

        # raise ValueError(node.get_code())
        node = _apply_formatting(node)
        # raise ValueError(node.get_code())

        _insert_or_append(node, graph, assignment)

        return graph.get_code()


def _is_comma(node):
    return isinstance(node, tree.Operator) and node.value == ","


def _is_list_root_definition(node):
    return isinstance(node, tree.PythonNode) and node.type == "testlist_comp"


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

        return True

    def _iter_inner_entries(node):
        for child in parso_helper.iter_nested_children(node):
            if isinstance(child, tree.PythonNode) and child.type == "atom":
                yield child

    node = copy.deepcopy(node)

    for child in parso_helper.iter_nested_children(node):
        if isinstance(child, tree.Operator) and child.value == ",":
            child.prefix = ""
        elif hasattr(child, "prefix") and _needs_space(child):
            child.prefix = " "

    for child in _iter_inner_entries(node):
        opening_brace = child.children[0]
        opening_brace.prefix = "\n    "

    node.children[-1].prefix = "\n"

    return node
