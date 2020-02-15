#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The main class used for a regular `from foo import bar` Python import."""

import operator

from python_compatibility import iterbot
from parso_helper import node_seek
from parso.python import tree

from .. import import_helper
from . import base as base_


class ImportFromAdapter(base_.BaseAdapter):
    """The main class used for a regular `from foo import bar` Python import."""

    @staticmethod
    def _get_namespaces(node):
        """Find every dot-separated namespace that this instance encapsulates.

        Args:
            node (:class:`parso.python.tree.ImportFrom`):
                Some node that may have one-or-more imports.

        Returns:
            set[str]: Dot-separated namespaces such as {"foo.bar.bazz", "foo.bar.thing"}.

        """
        namespaces = set()

        for path in node.get_paths():
            namespaces.add(".".join(map(operator.attrgetter("value"), path)))

        return namespaces

    @staticmethod
    def _partially_replace_namespace(base_names, old_parts, new_parts, prefix):
        """Replace part (but not all) of a from-import.

        Args:
            base_names (iter[:class:`parso.python.tree.Name`]):
                The nodes that represent some Python import namespace.
            old_parts (iter[str]):
                Some tokens that should match with all or part of `names`,
                in the same order. This parameter is used to figure out if
                any part of `names` will be overwritten by other functions.
            new_parts (list[str]):
                The namespace to replace `node` with. e.g. ["foo", "bar"].
            prefix (str):
                Leading whitespace that will be added to the new import nodes.

        """
        start, end = import_helper.get_replacement_indices(base_names, old_parts)
        new_nodes = import_helper.make_replacement_nodes(new_parts, prefix)

        base_names[0].parent.children[start : end + 1] = new_nodes

    def _replace_base_and_parts_of_tail(self, node, old_parts, new_parts, base_names, prefix):
        """Replace the first half of a from-import and any part of the end, if possible.

        Args:
            node (:class:`parso.python.tree.ImportFrom`):
                A parso object that represents a Python from-import.
            old_parts (iter[str]):
                Some tokens that should match with all or part of `names`,
                in the same order. This parameter is used to figure out if
                any part of `names` will be overwritten by other functions.
            new_parts (list[str]):
                The namespace to replace `node` with. e.g. ["foo", "bar"].
            base_names (iter[:class:`parso.python.tree.Name`]):
                The nodes that represent some Python import namespace.
            prefix (str):
                Leading whitespace that will be added to the new import nodes.

        """
        old_namespaces = {old for old, _ in self._namespaces}

        if not self._partial and not _has_fully_described_namespace(self._get_namespaces(node), old_namespaces):
            # We need to split the import statement in two
            new_nodes = import_helper.make_replacement_nodes(new_parts[:-1], prefix)
            children = _get_tail_children(node.children[3:])
            _adjust_imported_names(old_parts[-1], new_parts, children)

            return

        # Replace "from foo.bar.thing import something"
        new_nodes = import_helper.make_replacement_nodes(new_parts[:-1], prefix)
        _fully_replace_base(base_names, new_nodes)
        children = _get_tail_children(node.children[3:])
        _maybe_replace_imported_names(old_parts[-1], new_parts[-1], children)

    def _replace(self, node, old_parts, new_parts):
        """Change `node` from `old_parts` to `new_parts`.

        Warning:
            This method directly modifies `node`.

        The logic of this function is a bit intense. It goes something like this.

        - If `old_parts` fully describes the "from foo.bar.thing" part of `node`
            - completely replace "foo.bar.thing" with whatever `new_parts` is.
        - If `old_parts` goes beyond "from foo.bar.thing" and actually
          starts touching the namespaces of "from foo.bar.thing import something".
            - replace both "foo.bar.thing" and "something" with the new namespace.
        - If `old_parts` only partiall describes `node`.
            - figure out what parts of "from foo.bar.thing" should be replaced or kept

        Args:
            node (:class:`parso.python.tree.ImportFrom`):
                A parso object that represents a Python import.
            old_parts (list[str]):
                The namespace that is expected to be all or part of the
                namespace that `node` defines.
            new_parts (list[str]):
                The namespace to replace `node` with. e.g. ["foo", "bar"].

        """
        base_names = _get_base_names(node.children[1])
        prefix = base_names[0].prefix

        if self._partial and _old_parts_equals_base(base_names, old_parts):
            # Replace "from foo.bar.thing"
            new_nodes = import_helper.make_replacement_nodes(new_parts, prefix)
            _fully_replace_base(base_names, new_nodes)

            return

        if _old_parts_exceeds_base(base_names, old_parts):
            self._replace_base_and_parts_of_tail(node, old_parts, new_parts, base_names, prefix)

            return

        if not self._partial:
            return

        self._partially_replace_namespace(base_names, old_parts, new_parts, prefix)

    @staticmethod
    def is_valid(node):
        """Check if `node` is compatible with this class.

        Args:
            node (:class:`parso.python.tree.ImportFrom`):
                A parso node. Any unrecognized type will return False.

        Returns:
            bool: If `node` is the right type.

        """
        return isinstance(node, tree.ImportFrom)

    @staticmethod
    def get_import_type():
        """str: An identifier used to categorize instances of this class."""
        return "import_from"


def _has_fully_described_namespace(required_namespaces, user_provided_namespaces):
    """Check if every namespace that needs to exist is in another list of namespaces.

    If the user is doing a non-partial replacement, that means every namespace
    that the from-import adds must have some old / new pair to be replaced with.

    Args:
        required_namespaces (iter[str]):
            The Python dot-separated namespaces that must exist. These
            namspaces should be every import that from a from-import.
            e.g. "from foo import bar, bazz", this would be
            {"foo.bar", "foo.bazz"}.
        user_provided_namespaces (set[str]):
            The Python dot-separated namespaces that a person should
            have provided to the :class:`ImportFromAdapter`.

    Returns:
        bool: If every namespace in `required_namespaces` is in `user_provided_namespaces`.

    """
    for namespace in required_namespaces:
        if namespace not in user_provided_namespaces:
            return False

    return True


def _fully_replace_base(base_names, nodes):
    """Replace ever node in `base_names` with a new Python namespace.

    Args:
        base_names (list[:class:`parso.python.tree.Name`]):
            The tokens (in parso form) of a Python import namespace. But
            without the dots.
        nodes (list[:class:`parso.python.tree.Name` or :class:`parso.python.tree.Operator`]):
            The converted nodes of `parts`.

    """
    parent = base_names[0].parent

    indices = {parent.children.index(child) for child in base_names}
    start = min(indices)
    end = max(indices)

    parent.children[start : end + 1] = nodes


def _maybe_replace_imported_names(old, new, nodes):
    """Replace every node in `nodes` with `new`, if its text is `old`.

    Args:
        old (str):
            The name of an import namespace that may be inside `nodes`.
        new (str):
            The namespace to replace `old` with, if it exists.
        nodes (iter[:parso.python.tree.Name`]):
            The ends of a from-import to potentially replace.
            e.g. with an import like "from foo import bar, thing",
            this would be [tree.Name("bar"), tree.Name("thing")].

    """
    for current_ending_node in nodes:
        if current_ending_node.value == old:
            current_ending_node.value = new


def _get_base_names(base):
    """Get every token of a Python import, as parso nodes.

    Args:
        base (:class:`parso.python.tree.Name` or :class:`parso.python.tree.PythonNode`):
            Either a full Python namespace import or a part of one.

    Returns:
        list[:class:`parso.python.tree.Name`]:
            Find every token that is part of a Python import.

    """
    if hasattr(base, "children"):
        base_children = base.children
    else:
        base_children = [base]

    return [name for name in base_children if isinstance(name, tree.Name)]


def _get_tail_children(nodes):
    """Get the tail namespaces of a from-import.

    In other words, from "from foo import bar, thing", get the "bar" and "thing".

    Args:
        nodes (iter[:class:`parso.python.tree.PythonBaseNode`]):
            All parso objects that represent a Python from-import's
            tail. It may contain commas and other syntax-specific parts.
            But this will all be filtered out before being returned.

    Returns:
        list[:class:`parso.python.tree.PythonBaseNode`]: The found tail nodes.

    """
    children = []

    for node in nodes:
        if isinstance(node, tree.PythonNode) and node.type == "import_as_names":
            children.extend(
                [child for child in node.children if isinstance(child, tree.Name)]
            )
        elif not isinstance(node, tree.Operator):
            children.append(node)

    return children


def _old_parts_equals_base(base_names, parts):
    """Check if `parts` describes the given parso nodes exactly and nothing more.

    Most of the time, `parts` will describe all of `base_names` plus
    some extra Python namespace. In those situations, this function
    returns False. It only returns true if it matches exactly (with no
    extra namespace data).

    Args:
        base_names (list[:class:`parso.python.tree.Name`]):
            The parso nodes that represent a Python import (but with no "."s).

    Returns:
        bool: If `parts` is the same as `base_names`.

    """
    base_namespace = [name.value for name in base_names]

    return base_namespace == parts


def _old_parts_exceeds_base(base_names, parts):
    """Check if `parts` describes all of `base_names` plus extra data.

    Args:
        base_names (list[:class:`parso.python.tree.Name`]):
            The parso nodes that represent a Python import (but with no "."s).

    Returns:
        bool: If `parts` is includes all of `base_names` + more data.

    """
    base_namespace = [name.value for name in base_names]

    return base_namespace == parts[:-1]


def _remove_comma(node):
    """Delete a sibling comma, assuming that `node` comes from a from-import.

    Args:
        node (:class:`parso.python.tree.Name`): Some part of a Python from-import.

    """
    parent = node.parent
    index = parent.children.index(node)

    if index + 1 > len(parent.children):
        # We're at the end of a sequence of imports e.g. "from foo import bar, bazz, another"
        del parent.children[index - 1]  # Delete the previous ","
        del parent.children[index - 1]  # Now delete the name

        return

    # We must be at the beginning or somewhere in the middle of the import.
    del parent.children[index]  # Remove the name
    del parent.children[index]  # Remove the trailing ","


def _adjust_imported_names(old, new_namespace, nodes):
    """Split a from-import into 2 separate import statements.

    Args:
        old (str):
            The tail of a from-import which will be split into its own import.
        new_namespace (list[str]):
            The items to use for a new import e.g. ["foo", "bar"].
        nodes (iter[:class:`parso.python.tree.Name`]):
            The tail of a from-import whose import namespaces will be split.

    """
    def _get_import_from(node):
        """Get the :class:`parso.python.tree.ImportFrom` parent of `node`."""
        previous = None

        while previous != node:
            if isinstance(node, tree.ImportFrom):
                return node

            previous = node
            node = node.parent

        return None

    def _adjust_prefix(node):
        """Put `node` on its own line but retain its original leading indent."""
        prefix_node = node_seek.get_node_with_first_prefix(node)
        original = prefix_node.prefix
        prefix_node.prefix = "\n{original}".format(original=original)

        return original

    def _make_import(namespace_parts, prefix=""):
        """Make a new from-import node and insert it into an existing parso graph.

        Args:
            namespace_parts (list[str]):
                The import that will be converted into a parso from-import node.
            prefix (str, optional):
                The leading whitespace (indentation) placed before the new import.

        Returns:
            :class:`parso.python.tree.ImportFrom`: A newly generated import statement.

        """
        base_names = namespace_parts[:-1]
        base_count = len(base_names)
        base_nodes = []

        if base_count > 1:
            for is_last, name in iterbot.iter_is_last(base_names):
                base_nodes.append(tree.Name(name, (0, 0)))

                if not is_last:
                    base_nodes.append(tree.Operator(".", (0, 0)))

            # TODO : Need a unittest for this block
            base_nodes[0].prefix = " "
            base = tree.PythonNode("dotted_name", base_nodes)
        else:
            base = tree.Name(base_names[0], (0, 0), prefix=" ")

        return tree.ImportFrom([
            tree.Keyword("from", (0, 0), prefix=prefix),
            base,
            tree.Keyword("import", (0, 0), prefix=" "),
            tree.Name(namespace_parts[-1], (0, 0), prefix=" "),
        ])

    def _add_new_import(node, new_namespace):
        """Add a new from-import of `new_namespace` as a sibling of `node`."""
        import_from = _get_import_from(node)
        parent = import_from.parent
        index = parent.children.index(import_from)

        prefix = _adjust_prefix(import_from)
        new_import_node = _make_import(new_namespace, prefix=prefix)

        parent.children.insert(index, new_import_node)

    for current_ending_node in nodes:
        if current_ending_node.value != old:
            continue

        _remove_comma(current_ending_node)
        _add_new_import(current_ending_node, new_namespace)

        return
