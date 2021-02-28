#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The main class used for a regular `import foo.bar.bazz` Python import.

It also covers `import thing, some, other.namespace, more.imports`.

"""

import itertools

from parso.python import tree
from parso_helper import node_seek

from .. import import_helper
from . import base as base_


class ImportNameAdapter(base_.BaseAdapter):
    """The main class used for a regular `import foo.bar.bazz` Python import."""

    @staticmethod
    def _get_namespaces(node):
        """Find every dot-separated namespace that this instance encapsulates.

        Args:
            node (:class:`parso.python.tree.PythonNode`):
                Some node that may have one-or-more imports.
                e.g. `import foo, bar.bazz, thing`.

        Returns:
            set[str]: Dot-separated namespaces such as {"foo", "bar.bazz", "thing"}.

        """
        pairs = _get_pairs(node.children)

        if not pairs:
            # This happens when the import doesn't contain commas
            return {_collapse_namespace(node.children)}

        namespaces = set()

        for start, end in pairs:
            # We do `start + 1` because the starting index is a `,` which we don't want
            nodes = node.children[start + 1 : end]

            if _is_nested_import_list(nodes):
                namespaces.add(_collapse_namespace(nodes[0].children))
            else:
                namespaces.add(_collapse_namespace(node.children[start + 1 : end]))

        return namespaces

    def _replace(self, node, old_parts, new_parts, namespaces=frozenset()):
        """Change `node` from `old_parts` to `new_parts`.

        Warning:
            This method directly modifies `node`.

        The logic of this function is fairly simple.

        - If `node` is an import like "import foo.bar.thing", process it directly.
        - If `node` has multiple namspaces, "import foo, bazz, os.path"
            - Split each namespace and process them individually.

        This function will not change `node` if `old_parts` does not match
        with the namespaces that `node` defines.

        Args:
            node (:class:`parso.python.tree.ImportFrom`):
                A parso object that represents a Python import.
            old_parts (list[str]):
                The namespace that is expected to be all or part of the
                namespace that `node` defines.
            new_parts (list[str]):
                The namespace to replace `node` with. e.g. ["foo", "bar"].

        """
        pairs = _get_pairs(node.children)

        if not pairs:
            _replace_namespace(
                node.children, old_parts, new_parts, partial=self._partial
            )

            return

        for start, end in pairs:
            nodes = node.children[start + 1 : end]

            if not _is_matching_prefix_namespace(nodes, old_parts):
                continue

            if not _is_nested_import_list(nodes):
                _replace_namespace(nodes, old_parts, new_parts, partial=self._partial)

                continue

            _replace_namespace(
                nodes[0].children, old_parts, new_parts, partial=self._partial
            )

    @staticmethod
    def is_valid(node):
        """Check if `node` can be processed by this class."""
        if not (
            _is_dotted_import(node)
            or (isinstance(node, tree.PythonNode) and node.type == "dotted_as_names")
        ):
            return False

        for parent in node_seek.iter_parents(node):
            if isinstance(parent, tree.ImportFrom):
                return False

        return True

    @staticmethod
    def get_import_type():
        """str: An identifier used to categorize instances of this class."""
        return "import_name"


def _is_dotted_import(node):
    """Check if `node` represents a Python import like "import foo.bar"."""
    return isinstance(node, tree.PythonNode) and node.type == "dotted_name"


def _is_matching_prefix_namespace(children, old_parts):
    """Check if a list of nodes matches an expected namespace completely.

    Args:
        children (list[:class:`parso.python.tree.PythonNode`]):
            The nodes to check which represent some import namespace.
            e.g. [Name("foo"), Operator("."), Name("bar")].
        old_parts (iter[str]):
            An import namespace like ["foo", "bar"].

    Returns:
        bool: If `children` is a namespace that starts with `old_parts`.

    """
    if _is_nested_import_list(children):
        children = children[0].children

    old_namespace = ".".join(old_parts)

    # `expected_namespace` may equal `old_namespace` or be a child
    # namespace or a completely unrelated namespace.
    #
    expected_namespace = "".join(
        [item.get_code(include_prefix=False) for item in children]
    )

    return expected_namespace.startswith(old_namespace)


def _is_nested_import_list(nodes):
    """Check if the given nodes define an inner, nested Python import.

    This function has a special use. Assuming you have an import like
    "import foo, thing.bar, another", this function is used to check if
    any of the 3 imports have a dot in them (aka is nested).

    Args:
        nodes (list[:class:parso.python.tree.PythonNode`):
            The parso nodes that may define a nested Python import namespace.

    Returns:
        bool: If nodes resembles "thing.bar" (has a dot), return True.

    """
    return len(nodes) == 1 and _is_dotted_import(nodes[0])


def _get_pairs(nodes):
    """Get the index of every comma in some Python import's children.

    Args:
        nodes (list[:class:`parso.python.tree.PythonBaseNode`]):
            These parso nodes are the children of another parso node.
            Presumably, the parent is from a parso node that defines a
            single Python import.

    Returns:
        list[tuple[int, int]]:
            Using commas as "splits", mark of the start and end
            index for every comma found in `nodes`. This return is
            inclusive, meaning that it includes a pair for the last
            import namespace. Meaning in an import like "import foo,
            bar, thing", a start / end part that describes ", thing" is
            returned with the other 2 pairs.

    """

    def _get_splits(nodes):
        splits = set()

        for index, child in enumerate(nodes):
            if isinstance(child, tree.Operator) and child.value == ",":
                splits.add(index)

        return splits

    splits = _get_splits(nodes)

    if not splits:
        return []

    splits = sorted(splits)
    base = [(splits[index - 1], splits[index]) for index in range(1, len(splits))]
    beginning = [(-1, splits[0])]
    remainder = [(splits[-1], len(nodes))]

    return beginning + base + remainder


def _collapse_namespace(nodes):
    """Make a Python dot-separated import using the given parso nodes.

    This function makes sure to strip away any extra information, like
    in-lined comments or whitespace.

    Args:
        nodes (iter[:class:`parso.python.tree.Name`]):
            Tokens that make up a Python import.
            e.g. [tree.Name("foo"), tree.Name("bar"), tree.Name("thing")].

    Returns:
        str: The generated Python import namespace. e.g. "foo.bar.thing".

    """
    items = []

    for child in nodes:
        if hasattr(child, "children"):
            items.append(_collapse_namespace(child.children))
        else:
            items.append(child.value)

    return "".join(items)


def _replace_namespace(nodes, old_parts, new_parts, partial=False):
    """Change `nodes` into an import resembling the Python namespace defined by `new_parts`.

    If there's no common namespace between `nodes` and `old_parts` then
    this function does nothing.

    Args:
        node (:class:`parso.python.tree.ImportFrom`):
            A parso object that represents a Python import.
        old_parts (list[str]):
            The namespace that is expected to be all or part of the
            namespace that `node` defines.
        new_parts (list[str]):
            The namespace to replace `node` with. e.g. ["foo", "bar"].

    """

    def _is_fully_defined_by(names, parts):
        for index, name in enumerate(names):
            try:
                part = parts[index]
            except IndexError:
                return False

            if part != name:
                return False

        return True

    names = [
        child
        for node in nodes
        for child in itertools.chain([node], node_seek.iter_nested_children(node))
        if isinstance(child, tree.Name)
    ]
    prefix = node_seek.get_node_with_first_prefix(names[0]).prefix
    start, end = import_helper.get_replacement_indices(names, old_parts)

    if start == -1 or end == -1:
        # There's nothing to replace, in this case
        return

    if not partial and not _is_fully_defined_by(
        [name.value for name in names], old_parts
    ):
        return

    new_nodes = import_helper.make_replacement_nodes(new_parts, prefix)
    names[0].parent.children[start : end + 1] = new_nodes
