#!/usr/bin/env python
# -*- coding: utf-8 -*-

import abc
import collections
import json

import six
from parso.python import tree
from rez import package_serialise
from rez.vendor.schema import schema


@six.add_metaclass(abc.ABCMeta)
class BaseAdapter(object):
    @staticmethod
    @abc.abstractmethod
    def check_if_invalid(data):
        return ""

    @staticmethod
    @abc.abstractmethod
    def modify_with_existing(graph, data):
        pass


class HelpAdapter(BaseAdapter):
    @staticmethod
    def check_if_invalid(data):
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

    @staticmethod
    def modify_with_existing(graph, data):
        raise NotImplementedError()


class TestsAdapter(BaseAdapter):
    @staticmethod
    def check_if_invalid(data):
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
    def modify_with_existing(cls, graph, data, package):
        def _bake_down_tests_data(data):
            # TODO : Again, in the future when parso is more fleshed out, we won't need this function
            output = dict()

            for key, value in data.items():
                if isinstance(value, collections.MutableMapping):
                    output[key] = _bake_down_tests_data(value)

                    continue
                elif key == "requires":
                    value = [str(request) for request in value]

                output[key] = value

            return output

        # TODO : In the future, make a parso function that collects
        # existing data using `graph` so that `package` is not needed
        # anymore.
        #
        # existing = _get_tests_data(graph)
        assignment = _find_assignment_nodes("tests", graph)

        if assignment and _is_binding(assignment):
            raise NotImplementedError("@early and @late functions are not supported.")

        existing = package.tests or dict()
        existing = _bake_down_tests_data(existing)
        new = dict()
        _update(new, existing)
        _update(new, data)
        node = _make_tests_node(sorted(new.items()))

        if assignment:
            node.children[
                0
            ].prefix = " "  # Add a space between "tests =" and the first "{"
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


def _find_assignment_nodes(attribute, graph):
    for child in _iter_nested_children(graph):
        if isinstance(child, tree.ExprStmt):
            for name in child.get_defined_names():
                if name.value == attribute:
                    return child

    return None


# def _get_tests_data(graph):
#     def _get_nodes_after_colon(start):
#         raise NotImplementedError()
#
#     try:
#         node = _find_assignment_nodes("tests", graph)[-1]
#     except IndexError:
#         return []
#
#     return list(_iter_nested_children(node))


# TODO : Might be worth moving to python_compatibility?
def _update(d, u):
    # Reference: https://stackoverflow.com/a/59685868/3626104
    if not isinstance(d, collections.MutableMapping):
        return u

    for k, v in u.iteritems():
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
    if isinstance(value, six.string_types):
        return _escape(value)
    elif isinstance(value, list):
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
        else:
            nodes.append(tree.String(_escape_all(value), (0, 0), prefix=" "))

        nodes.append(tree.Operator(",", (0, 0)))

    base = tree.PythonNode("dictorsetmaker", nodes)

    return tree.PythonNode(
        "atom",
        [tree.Operator("{", (0, 0)), base, tree.Operator("}", (0, 0), prefix="\n")],
    )
