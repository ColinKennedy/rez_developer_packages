#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The module used to parse and replace attribute name referenes in a Python file.

This module has lots of logic for automatically parsing Python modules,
finding relevant attribute information, and only replacing what needs t
o be replaced.

"""

import copy
import itertools
import logging

from parso.python import tree
from parso_helper import node_seek

from . import creator, parser

_LOGGER = logging.getLogger(__name__)


def _is_eligible(node):
    """Check if `node` is an import. If it is, then it is not eligible.

    Eligibility in this case means "A Python name node which is not
    meant to be replaced by some **other** module than this one".

    Since imports are replaced by other modules, we need to exclude them
    from functions which run in this module.

    Args:
        node (:class:`parso.python.tree.BaseNode`): Some node to check.

    Returns:
        bool:
            If this `node` is okay to treat as an attribute name and
            manipulate, return True. Otherwise, return false.

    """
    for parent in itertools.chain(
        node_seek.iter_parents(node), node_seek.iter_nested_children(node)
    ):
        if isinstance(parent, (tree.ImportName, tree.ImportFrom)):
            return False

    return True


def _get_module_and_attribute(namespace):
    """Get a module + attribute namespace to describe `namespace`.

    `namespace` could be fully qualified import space, like
    "foo.bar.bazz.thing".  But users would normally import that as
    `from foo.bar import bazz`.  This function gets the tail bit,
    "bazz.thing".

    Args:
        namespace (str): The full, qualified Python dot-separated namespace.

    Returns:
        str: The found module + name.

    """
    parts = namespace.split(".")

    return "{module}.{name}".format(module=parts[-2], name=parts[-1])


def _get_replacement_index(namespace, node):
    """Find the child index of `node` which defines all of `namespace`.

    Args:
        namespace (str):
            An attribute namespace to check for. This is **not** the
            fully qualified namespace of the attribute but the namespace
            which users would refer to that attribute in code.
        node (:class:`parso.python.tree.PythonNode`):
            A parso object to check for children for `namespace`.

    Returns:
        int: The found index, if any. If no index is found, -1 is returned.

    """
    count = len(node.children)

    for index in range(1, count + 1):
        copied = copy.deepcopy(node)
        copied.children[:] = copied.children[:index]

        if copied.get_code().strip() == namespace:
            if index + 1 >= count:
                return index

            child_index = 0

            for index_, child in enumerate(
                node_seek.iter_nested_children(node.children[index + 1])
            ):
                child_index = index_

                if not (
                    isinstance(child, tree.Operator) and child.value == "."
                ) and not isinstance(child, tree.Name):
                    break

            return index + child_index

    return -1


def _get_inner_python_node(node):
    """Find the node which represents the Python namespace which must be replaced.

    Args:
        node (:class:`parso.python.tree.PythonNode`):
            Some parent node which usually wraps the node which is
            actually needed to be replaced.

    Returns:
        :class:`parso.python.tree.PythonNode` or NoneType: The found node, if any.

    """
    previous = node

    while True:
        if not node.children:
            return previous

        child = node.children[0]

        # Get the first non-whitespace related child
        for index in range(len(node.children)):
            child = node.children[index]

            if not isinstance(child, tree.Newline):
                break

        if not isinstance(child, (tree.PythonNode, tree.ExprStmt)):
            return node

        previous = node
        node = child

    return None


def _get_tail(text):
    """str: Get the last part of dot-separated a namespace."""
    return text.split(".")[-1]


def _make_attribute_replacement(old, new, node):
    """Replace the `old` attribute with `new`.

    Args:
        old (str):
            The attribute namespace to replace from.
        new (str):
            The attribute namespace to change to.
        node (:class:`parso.python.tree.PythonNode`):
            The parso object which will be directly modified by this function.,

    """
    node = _get_inner_python_node(node) or node
    end = _get_replacement_index(old, node)

    if not new.needs_full_namespace():
        new_reference = new.get_reference_namespace() or new.get_full_namespace()
        tail = _get_module_and_attribute(new_reference)
    else:
        tail = new.get_full_namespace()

    prefix_node = node_seek.get_node_with_first_prefix(node)

    node.children[:end] = [tree.Name(tail, (0, 0), prefix=prefix_node.prefix)]


def _make_namespace_replacement(old, new, node):
    """Replace `node`'s `old` part with `new`.

    Args:
        old (str):
            The attribute namespace to replace.
        new (str):
            A tail attribue namespace to replace with.
        node (:class:`parso.python.tree.PythonNode`):
            The parso object which will be directly modified by this function.,

    """
    namespaces_in_node = parser.get_used_namespaces(
        node_seek.iter_nested_children(node)
    )
    found_namespaces = sorted(
        (namespace for namespace in namespaces_in_node if namespace.startswith(old)),
        key=len,
    )
    found_namespace = found_namespaces[-1]  # Get the longest match

    if found_namespace == old:
        replaced_namespace = new
    else:
        replaced_namespace = (
            new + "." + found_namespace[len(old) + 1 :]
        )  # `+ 1` removes a trailing "."

    parts = replaced_namespace.split(".")
    beginning = parts[0]
    endings = parts[1:]

    prefix_node = node_seek.get_node_with_first_prefix(node)

    end = _get_replacement_index(old, node)
    tail = node.children[end + 1 :]
    replacement = tree.PythonNode(
        "power",
        [tree.Name(beginning, (0, 0), prefix=prefix_node.prefix)]
        + [
            tree.PythonNode(
                "trailer", [tree.Operator(".", (0, 0)), tree.Name(value, (0, 0))],
            )
            for value in endings
        ]
        + tail,
    )

    node.parent.children[node.parent.children.index(node)] = replacement


def replace(attributes, graph, namespaces, partial=False):
    """Replace each old / new `attributes` pair in `graph`.

    Note:
        `namespaces` must be fully qualified imports.
        For a file like this:

        .. code-block:: python

            from foo import blah
            import thing

        `namespaces` would be `[("foo.blah", "some.new.foo"), ("thing", "another")]`

    Args:
        attributes (container[tuple[:class:`._Dotted`, :class:`._Dotted`]]):
            Each namespace attribute name and the value which is must be
            replaced by.
        graph (:class:`parso.tree.Module`):
            The root of the Python module which will be directly editted
            by this function.
        namespaces (container[str]):
            Each old / new import namespace pair which the user would
            like to substitute in `graph`, in **other** functions (not
            this one). This function uses this information to determine
            if a found parso Name node needs replacement.

    Returns:
        list[tuple[:class:`._Dotted`, :class:`._Dotted`]]:
            Each old namespace attribute and the namespace which replaced it.

    """

    def _get_closest_match(text, options):
        for option in sorted(options, key=len, reverse=True):
            if text.startswith(option):
                return option

        return ""

    changed = []

    for child in node_seek.iter_nested_children(graph):
        code = child.get_code().strip()

        if not isinstance(child, tree.PythonNode):
            continue

        node = _get_inner_python_node(child) or child

        if not _is_eligible(node):
            _LOGGER.debug('Node "%s" was not eligible so it was skipped.', node)

            continue

        for old, new in attributes:
            old_references = old.get_alias_references()
            old_reference = _get_closest_match(code, old_references)

            if not old_reference:
                continue

            _make_attribute_replacement(old_reference, new, node)
            changed.append((old, new))

            break

    for child in node_seek.iter_nested_children(graph):
        code = child.get_code().strip()

        if not isinstance(child, tree.PythonNode):
            continue

        node = _get_inner_python_node(child) or child

        if not _is_eligible(node):
            continue

        for old, new in namespaces:
            if partial:
                if not code.startswith(old):
                    continue
            else:
                if code != old:
                    continue

            new_tail = new.split(".")[-1]
            _make_namespace_replacement(old, new_tail, node)
            changed.append((old, new))

            break

    return changed


def add_imports(namespaces, graph, old_import_candidates=tuple(), existing=tuple()):
    """Add `namespaces` as imports to `graph` if they are missing.

    Args:
        namespaces (iter[str]):
            Each fully qualified import namespace to potentially add
            onto `graph` (but only if needed).
        graph (:class:`parso.tree.Module`):
            The root of the Python module which will be directly editted
            by this function.
        old_import_candidates (container[str], optional):
            Fully qualified imports. If any attribute name within
            `graph` is still in this list, an import will be added back
            into `graph`.
        existing (:class:`.BaseAdapter`, optional):
            An import description which already exists within `graph`.

    """
    imports = set(
        namespace for import_ in existing for namespace in import_.get_node_namespaces()
    )
    tails = set(_get_tail(import_) for import_ in imports)
    used_namespaces = parser.get_used_namespaces(
        [node for nodes in graph.get_used_names().values() for node in nodes],
    )

    # 1. If there's an attribute in the module that requires an import that
    # we don't have, add it back.
    #
    for import_ in old_import_candidates:
        if import_ in imports:
            continue

        tail = _get_tail(import_)

        for namespace in used_namespaces:
            if namespace.startswith(tail):
                node = creator.make_import_from_namespace(import_)
                graph.children.insert(0, tree.Newline("\n", (0, 0)))
                graph.children.insert(0, node)

    # 2. All remaining namespaces will be added as long as there's no
    #    import that does not already satify it.
    #
    for namespace in namespaces:
        module_namespace = namespace

        if "." in namespace:
            module_namespace = namespace.split(".")[-1]

        if module_namespace not in tails:
            node = creator.make_import_from_namespace(namespace)
            graph.children.insert(0, tree.Newline("\n", (0, 0)))
            graph.children.insert(0, node)