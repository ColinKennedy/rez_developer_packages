#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The parser module finds Rez package required dependencies."""

import re
import textwrap

from parso.python import tree

# Match any whitespace character but newline
#
# Reference: https://docs.python.org/3/library/re.html#regular-expression-syntax
#
_IS_INLINE_EXPRESSION = re.compile(r"[ \t\r\f\v]*#.+(?:\n\s*,)*")
_IS_COMMA_ON_NEXT_LINE = re.compile(r"\s*#.+(?:\n\s*,)*")
_COMMENT_EXPRESSION = re.compile(r"^\s*(?:#\s*)*#(?P<text>[^#]*)")
_MULTIPLE_NEWLINE_MATCH = re.compile(r"(?P<newlines>\n+)")


def _is_comment_on_same_line(node):
    """bool: Check if the parso node has an in-line comment next to it."""
    code = node.get_code()

    return bool(_IS_INLINE_EXPRESSION.match(code))


def _is_comma_on_next_lines(node):
    """bool: Check if the parso node is a list item that has a comma on a line below it."""
    code = node.get_code()

    return bool(_IS_COMMA_ON_NEXT_LINE.match(code))


def _get_comment_from_node(node):
    """Find a comment for the given "Rez requirement" parso node.

    Args:
        node (:class:`parso.python.tree.PythonBaseNode`):
            The parso node that may contain a Rez requirement string / variable.

    Returns:
        str: The found comment, if any exists.

    """

    def _remove_non_comment_ending(lines):
        for index, line in enumerate(lines):
            if not line.strip().startswith("#"):
                return lines[:index]

        return lines

    def _replace_newlines(match):
        newlines = match.group("newlines") or ""

        if len(newlines) < 2:
            return " "

        return newlines[:-1]  # Remove one newline

    code = node.get_code()
    lines = _remove_beginning_newlines(code.split("\n"))
    lines = _remove_non_comment_ending(lines)
    matches = [_COMMENT_EXPRESSION.match(line).group("text") for line in lines]

    if not matches:
        return ""

    clean_comment = "\n".join(matches).strip("\n")
    unindented_comment = textwrap.dedent(clean_comment)
    collapsed_comment = _MULTIPLE_NEWLINE_MATCH.sub(
        _replace_newlines, unindented_comment
    )

    return collapsed_comment


def _get_inline_comment(index, nodes):
    """Return a user comment for a Rez requirement.

    This function assumes that users have written comments like this

    .. code-block :: python

        requires = [
            "my_package",  # Some comment here
        ]

    Args:
        index (int):
            The starting position to use when looking for comments. is
            position should typically be the parso node that targets the
            "my_package" requirement string.
        nodes (list[:class:`parso.python.tree.PythonBaseNode`]):
            The parso nodes that make up the rest of ``requires``
            definition, all the way to the ending "]" operator.

    Returns:
        str: The found comment, if any.

    """
    # And the comments are added as prefixes to those nodes.
    #
    # So to get an in-line comment, we actually need to search
    # beyond the current node.
    #
    #
    comma_exists = False

    for node in nodes[index + 1 :]:
        if isinstance(node, tree.Operator) and node.value == ",":
            comma_exists = True
            comment = _get_comment_from_node(node)

            if comment and _is_comma_on_next_lines(node):
                return comment

        if not comma_exists:
            continue

        comment = _get_comment_from_node(node)

        if comment and comma_exists and _is_comment_on_same_line(node):
            return comment
        elif comment and (not comma_exists) and _is_comma_on_next_lines(node):
            return comment

        text = _get_requirement_text(node)

        if text:
            return ""

    return ""


def _get_multi_line_comment(node):
    """Find a comment for the given "Rez requirement" parso node.

    Args:
        node (:class:`parso.python.tree.PythonBaseNode`):
            The parso node that may contain a Rez requirement string / variable.

    Returns:
        str: The found comment, if any exists.

    """
    return _get_comment_from_node(node)


def _get_requirement_text(node):
    """Find the Rez package requirement from a parso node.

    Args:
        node (:class:`parso.python.tree.PythonBaseNode`):
            The parso node that may contain a Rez requirement string / variable.

    Returns:
        str: The requirement data found, if any.

    """
    if isinstance(node, tree.Name):
        # This happens when the users write a constant variable
        return node.name

    if isinstance(node, tree.String):
        # The most common occurrence - people just write the requirement as a string
        #
        # Remove the surrounding ""s of the string
        #
        return node.value.strip("'").strip('"')

    return ""


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
        return
        yield  # pylint: disable=unreachable

    for child in node.children:
        if child not in seen:
            seen.add(child)

            yield child

            for subchild in _iter_nested_children(child):
                yield subchild


def _remove_beginning_newlines(lines):
    """Remove any leading newlines in a list of Python source code.

    Args:
        lines (list[str]):
            The Python source code, (usually comments) that will be removed.

    Returns:
        list[str]: The same `lines`, but now any empty starting lines are removed.

    """
    first_non_blank_line = 0

    for line in lines:
        if line.strip():
            break

        first_non_blank_line += 1

    return lines[first_non_blank_line:]


def get_full_name_definition(node):
    """Find every node related to a Rez package ``requires`` definition.

    This function assumes that ``requires`` is a list, not its functional form.

    Args:
        node (:class:`parso.python.tree.PythonBaseNode`):
            The node that marks the beginning of a ``requires``
            definition. Usually, this is Name node to ``requires``,
            itself.

    Returns:
        list[:class:`parso.python.tree.PythonBaseNode`]: The found nodes.

    """

    def _is_end(node):
        return isinstance(node, tree.Operator) and node.value == "]"

    nodes = []
    current = node

    while not _is_end(current):
        nodes.append(current)
        current = current.get_next_leaf()

    if current not in nodes:
        nodes.append(current)

    return nodes


def get_comment_pairs(nodes):
    """Get every string and its comment.

    Args:
        nodes (list[:class:`parso.python.tree.PythonBaseNode`]):
            The parsed code of a Python file. This will usually be the
            ``requires`` list that just about every package.py defines.

    Returns:
        dict[str, str]:
            The string or variable name and its commented value.
            e.g. {"rez-2+": "The best thing to happen since sliced bread!"}.

    """
    pairs = dict()

    for index, node in enumerate(nodes):
        requirement = _get_requirement_text(node)

        if not requirement:
            continue

        comment = _get_inline_comment(index, nodes)

        if not comment:
            comment = _get_multi_line_comment(node)

        pairs[requirement] = comment

    return pairs


def find_named_node(graph, name):
    """Find a node (e.g. a Python attribute) in `graph` that matches `name`.

    Note:
        In Rez, most attributes can also be implemented as functions,
        using @early and @late bindings.

        This function will search for either standard and return the
        right node.

    Args:
        graph (:class:`parso.python.tree.PythonBaseNode`):
            A Rez package.py that may define `name`.

    Returns:
        :class:`parso.python.tree.Name` or :class:`parso.python.tree.Function` or NoneType:
            The found object or nothing, if the attribute is note found.

    """
    children = []

    for child in _iter_nested_children(graph):
        if isinstance(child, (tree.Name, tree.Function)):
            if hasattr(child, "name"):
                name_ = child.name
            else:
                name_ = child.value

            if name_ == name:
                children.append(child)

    if not children:
        return None

    return children[-1]


def trim_list_excess(nodes):
    """Remove nodes un-related to Rez ``requires`` and return those that remain.

    Args:
        nodes (list[:class:`parso.python.tree.PythonBaseNode`]):
            The nodes that contain the entire ``requires`` definition and
            possibly some other nodes that need to be removed.

    Returns:
        list[:class:`parso.python.tree.PythonBaseNode`]:
            The nodes that represent just the requirements + their
            comments. Basically, assuming ``requires`` is an attribute,
            this output will contain just the nodes that are within the []s.

    """

    def _find_brace(nodes, brace):
        for index, node in enumerate(nodes):
            if isinstance(node, tree.Operator) and node.value == brace:
                return index

        return -1

    def _find_close_brace(nodes):
        return _find_brace(nodes, "]")

    def _find_open_brace(nodes):
        return _find_brace(nodes, "[")

    open_index = _find_open_brace(nodes)
    close_index = _find_close_brace(nodes)

    return nodes[open_index + 1 : close_index + 1]
