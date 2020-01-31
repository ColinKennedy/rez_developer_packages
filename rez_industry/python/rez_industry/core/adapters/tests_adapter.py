#!/usr/bin/env python
# -*- coding: utf-8 -*-

import collections
import copy
import logging
import json

import parso
from parso.python import tree
from rez.vendor.schema import schema
from rez import package_serialise
import six

from . import base as base_

_LOGGER = logging.getLogger(__name__)


class TestsAdapter(base_.BaseAdapter):
    """A class that modifies a Rez package definition `tests` attribute."""

    @staticmethod
    def check_if_invalid(data):
        """Check that the incoming data will work as a `tests` attribute.

        Args:
            data (dict[str, str] or dict[str, dict[str, str or list]]):
                The tests attribute content to test.

        Returns:
            str: A message why `data` is invalid. If `data` is valid, return nothing.

        """
        try:
            package_serialise.package_serialise_schema.validate(
                {
                    "name": "",  # This key is required so we just give it nothing
                    "tests": data,
                }
            )
        except schema.SchemaError as error:
            return str(error)

        return ""

    @classmethod
    def modify_with_existing(cls, graph, data):
        # TODO : Change the name
        def _update_foo(existing, extras):
            if not isinstance(existing, collections.MutableMapping):
                return extras

            existing = copy.deepcopy(existing)

            for key, value in extras.items():
                if _is_parso_dict_instance(value):
                    dict_value = _make_makeshift_node_dict(value)
                    existing[key] = _update_foo(existing.get(key, dict()), dict_value)
                else:
                    existing[key] = value

            return existing

        def _override_tests(base, data):
            if not base:
                return data

            data_graph = parso.parse(json.dumps(data))
            _flatten_nodes(data_graph)
            data_pairs = _make_makeshift_node_dict(data_graph)

            return _update_foo(base, data_pairs)

        try:
            assignment = _find_assignment_nodes("tests", graph)[-1]
        except IndexError:
            _LOGGER.warning(
                'Graph "%s" has no assignment. Tests will be appended instead of inserted.',
                graph,
            )
            assignment = None

        if assignment and _is_binding(assignment):
            raise NotImplementedError("@early and @late functions are not supported.")

        if assignment:
            maker_root = _get_dict_maker_root(assignment)
            _flatten_nodes(maker_root)

        existing = _get_tests_data(graph)
        new = dict()
        new = copy.deepcopy(existing)
        new = _override_tests(new, data)
        node = _make_tests_node(sorted(new.items()))

        if assignment:
            # Add a space between "tests =" and the first "{"
            node.children[0].prefix = " "
            # Now replace whatever assignment there used to be with the modified parso node
            assignment.children[-1] = node
        else:
            graph.children.append(
                tree.PythonNode(
                    "assignment",
                    [tree.String("tests = ", (0, 0), prefix="\n\n")] + [node],
                )
            )

        return graph.get_code()


def _is_binding(node):
    return not isinstance(node, tree.ExprStmt)


def _is_empty_dict(node):
    def _is_close(node):
        if not isinstance(node, tree.Operator):
            return False

        return node.value == ")"

    def _is_open(node):
        if not isinstance(node, tree.Operator):
            return False

        return node.value == "("

    for child in _iter_nested_children(node):
        if (
            isinstance(child, tree.PythonNode)
            and child.type == "atom"
            and len(child.children) == 2
            and child.children[0].value == "{"
            and child.children[-1].value == "}"
        ):
            # If this happens, it means that `node` is an empty dict
            return True

        if isinstance(child, tree.Name) and child.value == "dict":
            # Check if `child` is `dict()`
            maybe_open = child.get_next_leaf()

            if _is_open(maybe_open) and _is_close(maybe_open.get_next_leaf()):
                return True

    return False


def _is_parso_dict_instance(value):
    if not isinstance(value, tree.PythonNode):
        return False

    if value.type != "atom":
        return False

    if value.children[0].value != "{":
        return False

    if value.children[-1].value != "}":
        return False

    return True


def _find_assignment_nodes(attribute, graph):
    nodes = []

    for child in _iter_nested_children(graph):
        if isinstance(child, tree.ExprStmt):
            for name in child.get_defined_names():
                if name.value == attribute:
                    column = name.start_pos[1]

                    if column == 0:
                        nodes.append(child)

    return nodes


def _get_dict_maker_root(node):
    for child in _iter_nested_children(node):
        if isinstance(child, tree.PythonNode) and child.type == "dictorsetmaker":
            # If this happens, it means that `node` is a non-empty dict
            return child

    return None


def _get_dict_maker_pairs(node):
    operators = []

    for index, child in enumerate(node.children):
        if isinstance(child, tree.Operator) and child.value == ":":
            operators.append(index)

    return [(node.children[index - 1], node.children[index + 1]) for index in operators]


def _get_tests_data(graph):
    graph = copy.deepcopy(graph)

    try:
        assignment = _find_assignment_nodes("tests", graph)[-1]
    except IndexError:
        return dict()

    node = _get_dict_maker_root(assignment)

    if not node and _is_empty_dict(assignment):
        return dict()

    pairs = _get_dict_maker_pairs(node)

    for key, value in pairs:
        key.prefix = ""
        key.value = key.value.strip("'\"")

        if hasattr(value, "children"):
            for child in value.children:
                if hasattr(child, "prefix"):
                    child.prefix = ""  # This will be reset later

        if hasattr(value, "prefix"):
            value.prefix = ""

    return {
        key.get_code(): _make_makeshift_node_dict(value)
        if _is_parso_dict_instance(value)
        else value
        for key, value in pairs
    }


def _make_makeshift_node_dict(node):
    data_node_root = _get_dict_maker_root(node)
    data_pairs = _get_dict_maker_pairs(data_node_root)

    return {key.value.strip("'\""): value for key, value in data_pairs}


# TODO : Might be worth moving to python_compatibility?
def _update(d, u):
    # Reference: https://stackoverflow.com/a/59685868/3626104
    if not isinstance(d, collections.MutableMapping):
        return u

    for k, v in u.items():
        if isinstance(v, collections.Mapping):
            d[k] = _update(d.get(k, type(v)()), v)
        else:
            d[k] = v

    return d


# TODO : This was copied from another package. Might be worth making a separate package?
def _iter_nested_children(node):
    """Find every child node of the given `node`, recursively.

    Args:
        node (:class:`parso.python.tree.PythonBaseNode`): The node to get children of.

    Yields:
        :class:`parso.python.tree.PythonBaseNode`: The found children.

    """

    def __iter_nested_children(node, seen=None):
        if not seen:
            seen = set()

        if not hasattr(node, "children"):
            return
            yield  # pylint: disable=unreachable

        for child in node.children:
            if child not in seen:
                seen.add(child)

                yield child

                for subchild in __iter_nested_children(child, seen=seen):
                    yield subchild

    for child in __iter_nested_children(node):
        yield child


def _escape(key):
    return '"{key}"'.format(key=key.replace('"', '"'))


def _escape_all(value):
    if hasattr(value, "get_code"):
        return value.get_code()

    if isinstance(value, six.string_types):
        return _escape(value)

    if isinstance(value, list):
        return json.dumps(value)  # JSON will escape ' to "s for us

    return str(value)


def _make_dict_nodes(data, prefix=""):
    nodes = []

    for key, item in data:
        item = _escape_all(item)

        nodes.extend(
            [
                tree.String(
                    _escape(key), (0, 0), prefix="\n    {prefix}".format(prefix=prefix)
                ),
                tree.Operator(":", (0, 0)),
                tree.PythonNode(
                    "atom",
                    [
                        tree.String(item, (0, 0), prefix=" "),
                        tree.Operator(",", (0, 0)),
                    ],
                ),
            ]
        ),

    return tree.PythonNode(
        "atom",
        [
            tree.Operator("{", (0, 0), prefix=" "),
            tree.PythonNode("dictorsetmaker", nodes),
            tree.Operator("}", (0, 0), prefix="\n    "),
        ],
    )


def _flatten_nodes(data_graph):
    for child in _iter_nested_children(data_graph):
        if hasattr(child, "prefix"):
            child.prefix = ""


def _make_tests_node(data):
    nodes = []

    for key, value in data:
        nodes.extend(
            [
                tree.String(_escape(key), (0, 0), prefix="\n    "),
                tree.Operator(":", (0, 0)),
            ]
        )

        if isinstance(value, collections.MutableMapping):
            nodes.append(_make_dict_nodes(sorted(value.items()), prefix="    "))
        elif hasattr(value, "get_code"):
            if hasattr(value, "prefix"):
                value.prefix = " "

            nodes.append(value)
        else:
            nodes.append(tree.String(_escape_all(value), (0, 0), prefix=" "))

        nodes.append(tree.Operator(",", (0, 0)))

    base = tree.PythonNode("dictorsetmaker", nodes)

    return tree.PythonNode(
        "atom",
        [tree.Operator("{", (0, 0)), base, tree.Operator("}", (0, 0), prefix="\n")],
    )
