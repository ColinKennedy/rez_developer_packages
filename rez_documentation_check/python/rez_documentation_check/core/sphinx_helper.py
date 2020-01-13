#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""A series of parsing-related functions for changing existing a Sphinx conf.py file."""

import os
import pprint
import re

import parso
import six
from parso.python import tree  # pylint: disable=ungrouped-imports
from python_compatibility.sphinx import conf_manager, exceptions

_MAPPING_EXPRESSION = re.compile(
    r"^intersphinx_mapping\s*=\s*{}", re.DOTALL | re.MULTILINE
)
_INTERSPHINX_TEMPLATE = "intersphinx_mapping = {intersphinx_mapping}"


def _is_dict(node):
    """Check if the parso node defines a dict.

    Args:
        node (:class:`parso.python.tree.Node`): The node to check.

    Returns:
        bool: If `node` is actually a dict literal.

    """
    return isinstance(node, tree.PythonNode) and node.type == "dictorsetmaker"


def _is_intersphinx_assignment(node):
    """Check if a parso node assigns the ``intersphinx_mapping`` conf.py attribute.

    This function supports 3 methods of assignment.

    .. code-block:: python

        intersphinx_mapping = dict()

    .. code-block:: python

        intersphinx_mapping, foo = [dict(), None]

    .. code-block:: python

        intersphinx_mapping = foo = dict()


    Args:
        node (:class:`parso.python.tree.Node`): The parso node to check.

    Returns:
        bool:
            If True, the given node defins ``intersphinx_mapping``.
            Otherwise, return False.

    """
    if not isinstance(node, tree.PythonNode):
        return False

    if node.type != "simple_stmt":
        return False

    for child in _iter_nested_children(node):
        if isinstance(child, tree.Name) and child.value == "intersphinx_mapping":
            return True

    return False


def _make_intersphinx_dict(pairs):
    """Create a parso literal that defines ``intersphinx_mapping``.

    Args:
        pairs (list[:class:`parso.python.tree.Node`]):
            The key / value dict pairs that will be added into a new
            ``intersphinx_mapping`` dict literal.

    Returns:
        :class:`parso.python.tree.PythonNode`: The generated dict.

    """
    return tree.PythonNode(
        "atom",
        [
            tree.Operator("{", (0, 0), prefix=" "),
            tree.PythonNode("dictorsetmaker", pairs),
            tree.Operator("}", (len(pairs), 0), prefix="\n"),
        ],
    )


def _make_intersphinx_pairs(pairs):
    """Convert key/value pairs into something that parso can convert into dict key/values.

    Args:
        pairs (iter[tuple[str, str or tuple[str, str or NoneType]]):
            The intersphinx key/value mapping. Keys are usually the
            name of Rez packages and each value is the URL to the API
            documentation that we need to link to.

    Returns:
        list[:class:`parso.python.tree.Node`]:
            The key/value pairs, flattened into parso objects.

    """
    output = []

    for row, (key, value) in enumerate(sorted(pairs)):
        if isinstance(key, six.string_types):
            key = '"{key}"'.format(key=key)

        if isinstance(value, six.string_types):
            value = '"{value}"'.format(value=value)

        key_length = len(key)
        value_length = len(value)
        output.append(tree.String(key, (row, 0), prefix="\n    "))
        output.append(tree.Operator(":", (row, key_length)))
        output.append(tree.String(str(value), (row, key_length + len(":")), prefix=" "))
        output.append(tree.Operator(",", (row, key_length + len(":") + value_length)))

    return output


def _iter_nested_children(node, seen=None):
    """Find every child node of the given `node`, recursively.

    Args:
        node (:class:`parso.python.tree.PythonBaseNode`):
            The node to get children of.
        seen (set[:class:`parso.python.tree.PythonBaseNode`]):
            The nodes that have already been checked.

    Yields:
        :class:`parso.python.tree.PythonBaseNode`: The found children.

    """
    if not seen:
        seen = set()

    if not hasattr(node, "children"):
        yield
        return

    for child in node.children:
        if child not in seen:
            seen.add(child)

            yield child

            for subchild in _iter_nested_children(child):
                yield subchild


def _change_intersphinx_assignments(node, links):
    """Mutate a parso node into a intersphinx dict mapping.

    Args:
        node (:class:`parso.python.tree.PythonNode`):
            The that assigns ``intersphinx_mapping``. It will be
            overwritten with new node children.
        links (dict[str, str or tuple[str, str or NoneType]]):
            The intersphinx key / URL pairs to add onto `node`.

    Raises:
        RuntimeError: If no ``intersphinx_mapping`` is detected in `node`.

    """

    def _find_equals_index(node):
        """Find the index of the "=" operator."""
        children = node.children

        for index, child in enumerate(reversed(children)):
            if isinstance(child, tree.Operator) and child.value == "=":
                return len(children) - index

        return -1

    changed = False

    for child in reversed(node.children):
        if isinstance(child, tree.ExprStmt):
            index = _find_equals_index(child)

            if index == -1:
                raise RuntimeError(
                    "Expression was found but the assignment operator was not found."
                )

            child.children[:] = child.children[:index]  # Clear the existing assignment
            pairs = _make_intersphinx_pairs(links.items())
            child.children.append(_make_intersphinx_dict(pairs))
            changed = True

    if not changed:
        raise RuntimeError(
            "No intersphinx_mapping attribute was found so nothing was changed."
        )


def _replace_inline(links, path):
    """Update every ``intersphinx_mapping`` assignment with the given `links`.

    Args:
        links (dict[str, str or tuple[str, str or NoneType]]):
            The key / URL pairs that link to other Sphinx documentation projects.
        path (str):
            The path to a conf.py file on-disk that will be appended to.

    """
    with open(path, "r") as handler:
        code = handler.read()

    graph = parso.parse(code)

    for node in _iter_nested_children(graph):
        if not _is_intersphinx_assignment(node):
            continue

        _change_intersphinx_assignments(node, links)

    with open(path, "w") as handler:
        handler.write(graph.get_code())


def _append_to_end(links, path):
    """Add the ``intersphinx_mapping`` to the end of a conf.py file.

    Args:
        links (dict[str, str or tuple[str, str or NoneType]]):
            The key / URL pairs that link to other Sphinx documentation projects.
        path (str):
            The path to a conf.py file on-disk that will be appended to.

    """
    with open(path, "r") as handler:
        code = handler.read()
        needs_newline = code and not code.endswith(os.linesep)

    with open(path, "a") as handler:
        text = (
            _INTERSPHINX_TEMPLATE.format(
                intersphinx_mapping=pprint.pformat(links, indent=4)
            )
            + "\n"
        )

        if needs_newline:
            text = "\n" + text

        handler.write(text)


def replace_intersphinx_mapping(links, path):
    """Replace or append ``intersphinx_mapping`` with the `links` data.

    Args:
        links (dict[str, str or tuple[str, str or NoneType]]):
            The key / URL pairs that link to other Sphinx documentation projects.
        path (str):
            The path to a conf.py file on-disk that will be appended to.

    Raises:
        :class:`.SphinxFileBroken`: If `path` is not a valid Python file.

    """
    try:
        module = conf_manager.import_conf_file(path)
    except SyntaxError:
        raise exceptions.SphinxFileBroken(
            'conf.py "{path}" has a syntax error. Cannot continue.'.format(path=path)
        )

    if hasattr(module, "intersphinx_mapping"):
        _replace_inline(links, path)

        return

    _append_to_end(links, path)
