#!/usr/bin/env python
# -*- coding: utf-8 -*-

import copy

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


def _make_import_node(namespace):
    if "." not in namespace:
        return tree.PythonNode("simple_stmt", [tree.Import("import {namespace}".format(namespace=namespace))])

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
            tree.Newline("\n", (0, 0)),
        ],
    )


def replace(attributes, graph):
    changed = []

    for child in node_seek.iter_nested_children(graph):
        if not isinstance(child, tree.PythonNode):
            continue

        code = child.get_code().strip()

        for old, new in attributes:
            if code != old:
                continue

            tail = _get_module_and_attribute(new)
            prefix_node = node_seek.get_node_with_first_prefix(child)
            children = child.parent.children
            current = children[children.index(child)]

            ender = _get_ender(current)
            new_child_contents = [tree.Name(tail, (0, 0), prefix=prefix_node.prefix)]

            if ender:
                new_child_contents.append(ender)

            children[children.index(child)] = tree.PythonNode(
                "simple_stmt",
                new_child_contents,
            )

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
            graph.children.insert(0, node)

            break
