#!/usr/bin/env python
# -*- coding: utf-8 -*-

import copy

from parso_helper import node_seek
from parso.python import tree

from . import creator


def _get_ender(node):
    for child in reversed(list(node_seek.iter_nested_children(node))):
        if isinstance(child, tree.Newline):
            return copy.deepcopy(node)

        return None


def _get_module_and_attribute(namespace):
    parts = namespace.split(".")

    return "{module}.{name}".format(module=parts[-2], name=parts[-1])


def _get_replacement_range(namespace, node):
    for index in range(1, len(node.children) + 1):
        copied = copy.deepcopy(node)
        copied.children[:] = copied.children[:index]

        if copied.get_code().strip() == namespace:
            return index

    return -1


def _make_import_node(namespace):
    if "." not in namespace:
        return creator.make_import(namespace)

    base, tail = namespace.rsplit(".", 1)

    return creator.make_from_import_using_parts(base, tail)


def _get_inner_python_node(node):
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


def _make_attribute_replacement(old, new, node):
    node = _get_inner_python_node(node) or node
    end = _get_replacement_range(old, node)

    tail = _get_module_and_attribute(new)
    prefix_node = node_seek.get_node_with_first_prefix(node)
    children = node.parent.children
    current = children[children.index(node)]

    ender = _get_ender(current)
    new_child_contents = [tree.Name(tail, (0, 0), prefix=prefix_node.prefix)]

    if ender:
        new_child_contents.append(ender)

    node.children[:end] = [tree.Name(tail, (0, 0), prefix=prefix_node.prefix)]


def _make_namespace_replacement(old, new, node):
    names = []

    for child in node_seek.iter_nested_children(node):
        if isinstance(child, tree.Name):
            names.append(child)

    found_namespace = ".".join(name.value for name in names)

    if found_namespace == old:
        replaced_namespace = new
    else:
        replaced_namespace = new + "." + found_namespace[len(old) + 1:]  # `+ 1` removes a trailing "."

    parts = replaced_namespace.split(".")
    beginning = parts[0]
    endings = parts[1:]

    prefix_node = node_seek.get_node_with_first_prefix(node)

    replacement = tree.PythonNode(
        "power",
        [tree.Name(beginning, (0, 0), prefix=prefix_node.prefix)]
        + [
            tree.PythonNode(
                "trailer",
                [tree.Operator(".", (0, 0)), tree.Name(value, (0, 0))],
            )
            for value in endings
        ],
    )

    node.parent.children[node.parent.children.index(node)] = replacement


def replace(attributes, graph, namespaces=tuple()):
    changed = []

    # TODO : Consider merging these for-loops into a single for-loop
    for child in node_seek.iter_nested_children(graph):
        code = child.get_code().strip()

        if not isinstance(child, tree.PythonNode):
            continue

        node = _get_inner_python_node(child) or child

        for old, new in attributes:
            if not code.startswith(old):
                continue

            _make_attribute_replacement(old, new, node)
            changed.append((old, new))

            break

    for child in node_seek.iter_nested_children(graph):
        code = child.get_code().strip()

        if not isinstance(child, tree.PythonNode):
            continue

        node = _get_inner_python_node(child) or child

        for old, new in namespaces:
            if not code.startswith(old):
                continue

            _make_namespace_replacement(old, new, node)
            changed.append((old, new))

            break

    return changed


def add_imports(namespaces, graph, existing=tuple()):
    imports = set(namespace for import_ in existing for namespace in import_.get_node_namespaces())

    for namespace in namespaces:
        module_namespace = namespace

        if "." in namespace:
            module_namespace, _ = namespace.rsplit(".", 1)

        if module_namespace not in imports:
            node = _make_import_node(module_namespace)
            imports.add(module_namespace)
            graph.children.insert(0, tree.Newline("\n", (0, 0)))
            graph.children.insert(0, node)

            break
