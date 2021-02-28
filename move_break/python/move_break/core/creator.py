#!/usr/bin/env python
# -*- coding: utf-8 -*-

from parso.python import tree
import six


def make_import(name, prefix=""):
    return tree.ImportName(
        [
            tree.Keyword("import", (0, 0), prefix=prefix),
            tree.Name(name, (0, 0), prefix=" "),
        ],
    )


def make_from_import_using_parts(base, tail, prefix=""):
    import_base = base

    if isinstance(base, six.string_types):
        base_nodes = [tree.Name(part, (0, 0)) for part in base.split(".")]

        for index in reversed(range(1, len(base_nodes), 1)):
            base_nodes.insert(index, tree.Operator(".", (0, 0)))

        base_nodes[0].prefix = " "
        import_base = tree.PythonNode("dotted_name", base_nodes)

    import_tail = tail

    if isinstance(tail, six.string_types):
        import_tail = tree.Name(tail, (0, 0), prefix=" ")

    return tree.PythonNode(
        "simple_stmt",
        [
            tree.ImportFrom(
                [
                    tree.Keyword("from", (0, 0), prefix=prefix),
                    import_base,
                    tree.Keyword("import", (0, 0), prefix=" "),
                    import_tail,
                ]
            ),
        ],
    )
