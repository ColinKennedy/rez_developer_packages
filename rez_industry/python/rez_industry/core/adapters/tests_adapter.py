#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The main class used to modify a Rez package's `tests` attribute."""

import collections
import copy
import json
import logging

import parso
import six
from parso.python import tree
from parso_helper import node_seek
from rez import package_serialise
from rez.vendor.schema import schema

from .. import encoder
from .. import convention, parso_utility
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
        """Add `data` to a parso node `graph`.

        Reference:
            https://github.com/nerdvegas/rez/wiki/Package-Definition-Guide#tests

        Args:
            graph (:class:`parso.python.Tree.PythonBaseNode`):
                Some node that may assignment an attribute called
                "tests". If "tests" assignment exists, it gets
                overwritten. If no assignment exists then a new
                assignment is appended to the end of the file.
            data (dict[str, str or dict[str, str or list[str]]]):
                Any values that'd typically define a Rez "tests"
                attribute. Basically anything is allowed, as long the
                Rez package schema considers it valid.

        Raises:
            NotImplementedError:
                If the user tries to pass a `graph` that has an declared
                "tests" function, using @early or @late bindings.

        Returns:
            str:
                The modified Python source code. It should resemble the
                source code of `graph` plus any serialized `data`.

        """
        graph = copy.deepcopy(graph)

        try:
            assignment = parso_utility.find_assignment_nodes("tests", graph)[-1]
        except IndexError:
            _LOGGER.warning(
                'Graph "%s" has no assignment. Tests will be appended instead of inserted.',
                graph,
            )
            assignment = None

        if assignment and _is_binding(assignment):  # pragma: no cover
            raise NotImplementedError("@early and @late functions are not supported.")

        existing = _get_tests_data(graph)
        new = dict()
        new = copy.deepcopy(existing)
        new = _override_tests(new, data)
        new = {key: _flatten_everything(value) for key, value in new.items()}
        node = _make_tests_node(sorted(new.items()))

        graph = convention.insert_or_append(node, graph, assignment, "tests")

        return graph.get_code()

    @staticmethod
    def remove_from_attribute(graph, data):
        """Delete `data` from `graph`, if it exists.

        Args:
            graph (:class:`parso.python.tree.Module`):
                The parso node that will contains a "tests" attribute
                that this function will modify.
            data (dict[str, str or dict[str, str or list[str]]]):
                Any values that'd typically define a Rez "tests"
                attribute. Basically anything is allowed, as long the
                Rez package schema considers it valid.

        Returns:
            str: The original `graph` but as a result of the deleted content.

        """
        raise NotImplementedError("This feature hasn't been added.")


def _is_binding(node):
    """bool: Check if `node` is not an assigment. e.g. `foo = bar` returns False."""
    return not isinstance(node, tree.ExprStmt)


def _is_empty_dict(node):
    """Check if the given parso `node` represents an initialized-but-empty assignment.

    Args:
        node (:class:`parso.python.tree.ExprStmt`): The assignment node to check.

    Returns:
        bool: Return False if `node` is a non-empty dict. Otherwise, return True.

    """

    def _is_close(node):
        if not isinstance(node, tree.Operator):
            return False  # pragma: no cover

        return node.value == ")"

    def _is_open(node):
        if not isinstance(node, tree.Operator):
            return False  # pragma: no cover

        return node.value == "("

    for child in node_seek.iter_nested_children(node):
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

    return False  # pragma: no cover


def _is_parso_dict_instance(value):
    """Check if `value` is a parso node that defines a dict.

    Parso normally defines a dict roughly as an "atom" PythonNode. Its
    children is another PythonNode, tagged as a "dictorsetmaker" and
    wrapped in "{}"s.

    This function is trying to define the outer "atom" PythonNode.

    Args:
        value (:class:`parso.python.tree.PythonBaseNode`):
            A Parso node that needs to be checked. Only a
            :class:`parso.python.tree.PythonNode` has a possibility of
            returning True (but even then it is not guaranteed).

    Returns:
        bool: If the given `value` defines the outer node that defines a dict.

    """
    if not isinstance(value, tree.PythonNode):
        return False

    if value.type != "atom":
        return False  # pragma: no cover

    if value.children[0].value != "{":
        return False

    if value.children[-1].value != "}":
        return False  # pragma: no cover

    return True


def _get_dict_maker_root(node):
    """Find the inner parso PythonNode that defines a Python dict.

    Args:
        node (:class:`parso.python.tree.PythonBaseNode`):
            A parso node that may or may not have a "dictorsetmaker"
            node as one of its children. Usually, this will actually be
            an "atom" type :class:`parso.python.tree.PythonNode`

    Returns:
        :class:`parso.python.tree.PythonNode` or NoneType:
            Get the inner dict, if any exists in `node`.

    """
    for child in node_seek.iter_nested_children(node):
        if isinstance(child, tree.PythonNode) and child.type == "dictorsetmaker":
            # If this happens, it means that `node` is a non-empty dict
            return child

    return None


def _get_dict_maker_pairs(node):
    """Get the key / value dict information from some parso node.

    Args:
        node (:class:`parso.python.tree.PythonNode`):
            The parso node that is the "inner-most" parso node, closest
            to the key / value pairs of a Python dict.

    Returns:
        list[
            tuple[
                :class:`parso.python.tree.PythonBaseNode`,
                :class:`parso.python.tree.PythonBaseNode`
            ]
        ]:
            The found parso key / value pairs of `node`.

    """
    operators = []

    for index, child in enumerate(node.children):
        if isinstance(child, tree.Operator) and child.value == ":":
            operators.append(index)

    return [(node.children[index - 1], node.children[index + 1]) for index in operators]


def _get_tests_data(graph):
    """Get all of the existing key / value information of a "tests" attribute.

    It's assumed that `graph` defines (or at least includes) a Rez
    package.py's contents.

    Args:
        graph (:class:`parso.python.tree.PythonBaseNode`):
            The root node that will be checked. Usually, this is a
            :class:`parso.python.tree.Module` but it doesn't have to be.

    Returns:
        dict[
            str,
            :class:`parso.python.tree.PythonBaseNode`
                or dict[str, :class:`parso.python.tree.PythonBaseNode`]
            ]:
            The existing tests data. If `graph` doesn't have assignment
            data then an empty dict is returned.

    """
    graph = copy.deepcopy(graph)

    try:
        assignment = parso_utility.find_assignment_nodes("tests", graph)[-1]
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
    """Find every key / value of a parso dict and partially cast it back to a Python object.

    Args:
        node (:class:`parso.python.tree.PythonBaseNode`):
            A parso node that may or may not have a "dictorsetmaker"
            node as one of its children. Usually, this will actually be
            an "atom" type :class:`parso.python.tree.PythonNode`

    Returns:
        dict[str, :class:`parso.python.tree.PythonBaseNode`]:
            The original `node`, but converted into actual Python keys.

    """
    data_node_root = _get_dict_maker_root(node)
    data_pairs = _get_dict_maker_pairs(data_node_root)

    return {key.value.strip("'\""): value for key, value in data_pairs}


def _update_partial_python_dict(existing, extras):
    """Add the contents of `extras` onto `existing`.

    If `existing` represents a dict-of-dicts, and an "inner" dict has
    a key that `extras` does not, that key is preserved. If both dicts
    have the same key `extras` is preferred.

    Reference:
        https://stackoverflow.com/a/59685868/3626104

    Args:
        existing (dict[str, :class:`parso.python.tree.PythonBaseNode`]):
            Some data that will be overwritten by `extras`.
        extras (dict[str, :class:`parso.python.tree.PythonBaseNode`]):
            Data to overlay onto `existing`.

    Returns:
        dict[str, :class:`parso.python.tree.PythonBaseNode`]: The merged data.

    """
    if not isinstance(existing, collections.MutableMapping):
        return extras

    existing = copy.deepcopy(existing)

    for key, value in extras.items():
        if _is_parso_dict_instance(value):
            dict_value = _make_makeshift_node_dict(value)
            existing[key] = _update_partial_python_dict(
                existing.get(key, dict()), dict_value
            )
        else:
            existing[key] = value

    return existing


def _override_tests(base, data):
    """Add `data` onto `base`, while prioritizing anything in `data` over `base`.

    Args:
        base (dict[str, :class:`parso.python.tree.PythonBaseNode`]):
            The existing data that comes from a Rez package.py file.
            Since the "tests" attribute of a Rez package is always a
            dict, `base` will always be a dict of key/value pairs.
        data (dict[str, str] or dict[str, dict[str, str or list]]):
            Any information that will be added over top of `base`.

    Returns:
        dict[str, :class:`parso.python.tree.PythonBaseNode`]: The merged data.

    """
    if not base:
        return data

    data_graph = parso.parse(json.dumps(data, cls=encoder.BuiltinEncoder))
    data_pairs = _make_makeshift_node_dict(data_graph)

    return _update_partial_python_dict(base, data_pairs)


def _escape(key):
    """Make some text into a double-quoted dict key string."""
    return '"{key}"'.format(key=key.replace('"', '"'))


def _escape_all(value):
    """Convert `value` into a string.

    Args:
        value (object): Some parso or Python object that needs to be made into a string.

    Returns:
        str: A string representation of `value`.

    """
    if hasattr(value, "get_code"):
        return value.get_code()

    if isinstance(value, six.string_types):
        return _escape(value)

    if isinstance(value, list):
        return json.dumps(value, cls=encoder.BuiltinEncoder)  # JSON will escape ' to "s for us

    return str(value)  # pragma: no cover


def _make_dict_nodes(data, prefix=""):
    """Create a parso node that represents the inner key / value pairs of a Python dict.

    In terms of the work needed to generate a Rez "tests" attribute,
    this function is used mainly to create the "inner dict" that a
    "tests" attribute frequently defines.

    Args:
        data (iter[tuple[str, str or list or :class:`parso.python.tree.PythonBaseNode`]]):

    Returns:
        :class:`parso.python.tree.PythonNode`:
            A node that defines the inside of a parso dict. This node
            is not equivalent to an actual dict and still needs to be
            wrapped with another :class:`parso.python.tree.PythonNode`
            to be valid.

    """
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
                    [tree.String(item, (0, 0), prefix=" "), tree.Operator(",", (0, 0))],
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


def _flatten_everything(data):
    """Remove all prefix / whitespace information, wherever possible.

    Args:
        node (:class:`parso.python.tree.PythonBaseNode` or dict[str]):
            A parso object that presumably has whitespace or a dict of
            parso values.

    Returns:
        :class:`parso.python.tree.PythonBaseNode` or dict[str]:
            The original `node` given, but without whitespace.

    """
    if not isinstance(data, collections.MutableMapping):
        return _flatten_node(data)

    return {key: _flatten_node(value) for key, value in data.items()}


def _flatten_node(node):
    """Remove all prefix / whitespace information from a parso node + its children.

    :class:`TestsAdapter` is responsible for setting + appending
    whitespace for all of the parso nodes that eventually get written
    to disk. But existing data may already have whitespace prefix data.
    So this function sets that all back to zero, to make it easier to
    append a prefix to existing nodes.

    Args:
        node (:class:`parso.python.tree.PythonBaseNode`):
            A parso object that presumably has child nodes. These
            children may have whitespace - every child's whitespace will
            be removed.

    Returns:
        :class:`parso.python.tree.PythonBaseNode`:
            A copy of `node` whose children have no defined whitespace.

    """
    node = copy.deepcopy(node)

    if hasattr(node, "prefix"):
        node.prefix = ""

    for child in node_seek.iter_nested_children(node):
        if hasattr(child, "prefix"):
            child.prefix = ""

    return node


def _make_tests_node(data):
    """Create the final "tests" data that will be written to a package.py file.

    Important:
        This function technically doesn't create a "correct"
        parso dict. For the sake of simplicity, some corners were
        cut. For example, value data is converted into a raw
        :class:`parso.python.tree.String`. It's not technically
        "correct" but since this function is called just before writing
        the data into disk and not further modified, it's okay.

    Args:
        data (iter[str, :class:`parso.python.tree.PythonBaseNode`]):
            The key / value information that will be converted into a
            parso dict.

    Returns:
        :class:`parso.python.tree.PythonNode`:
            An atom PythonNode which has a full dictionary "tests"
            defined. This will later override an existing "tests"
            attribute in a package.py or be appended to the file as an
            assignment.

    """
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
