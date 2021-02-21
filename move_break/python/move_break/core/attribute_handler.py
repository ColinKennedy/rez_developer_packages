#!/usr/bin/env python
# -*- coding: utf-8 -*-

import copy
import itertools

from parso_helper import node_seek
from parso.python import tree


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
        return tree.ImportName(
            [
                tree.Keyword("import", (0, 0)),
                tree.Name(namespace, (0, 0), prefix=" "),
            ],
        )

    base, tail = namespace.rsplit(".", 1)
    base_nodes = [tree.Name(part, (0, 0)) for part in base.split(".")]

    for index in reversed(range(1, len(base_nodes), 1)):
        base_nodes.insert(index, tree.Operator(".", (0, 0)))

    base_nodes[0].prefix = " "

    return tree.PythonNode(
        "simple_stmt",
        [
            tree.Keyword("from", (0, 0)),
            tree.PythonNode("dotted_name", base_nodes),
            tree.Keyword("import", (0, 0), prefix=" "),
            tree.Name(tail, (0, 0), prefix=" "),
        ],
    )


def _get_inner_python_node(namespace, node):
    # for child in itertools.chain(node_seek.iter_nested_children(node), [node]):
    #     if not isinstance(child, tree.PythonNode):
    #         continue
    #
    #     if child.get_code().strip().startswith(namespace):
    #         return child
    #
    # return None
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

        if not isinstance(child, tree.PythonNode):
            return node

        previous = node
        node = child

    return None


def _make_namespace_replacement(old, new, node):
    node = _get_inner_python_node(old, node) or node
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


def replace(attributes, graph):
    changed = []

    for child in node_seek.iter_nested_children(graph):
        code = child.get_code().strip()

        if not isinstance(child, tree.PythonNode):
            continue

        for old, new in attributes:
            if not code.startswith(old):
                continue

            _make_namespace_replacement(old, new, child)
            changed.append((old, new))

            break

    return changed


def add_imports(namespaces, graph, existing=tuple()):
    imports = set(namespace for import_ in existing for namespace in import_.get_node_namespaces())

    for namespace in namespaces:
        module_namespace, _ = namespace.rsplit(".", 1)

        if module_namespace not in imports:
            node = _make_import_node(module_namespace)
            imports.add(module_namespace)
            graph.children.insert(0, tree.Newline("\n", (0, 0)))
            graph.children.insert(0, node)

            break
