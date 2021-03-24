#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""A module for creating import parso objects."""

import six
from parso.python import tree


def make_from_import_using_parts(base, tail, prefix="", alias=""):
    """Create a `from X import Y` object.

    Args:
        base (list[str] or str):
            The `from X` part of the import.
        tail (str):
            The `import Y` part of the import.
        prefix (str, optional):
            Leading whitespace to add to the beginning of the
            import. Default: "".

    Returns:
        :class:`parso.python.tree.PythonNode`: The created node.

    """
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

    if alias:
        import_tail = tree.PythonNode(
            "import_as_name",
            [
                import_tail,
                tree.Keyword("as", (0, 0), prefix=" "),
                tree.Name(alias, (0, 0), prefix=" "),
            ],
        )

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


def make_import(name, alias="", prefix=""):
    """Make a regular `import X` import.

    Args:
        name (str):
            The namespace to import.
        prefix (str, optional):
            Leading whitespace to add to the beginning of the
            import. Default: "".

    Returns:
        :class:`parso.python.tree.ImportName`:
            The created parso import object.

    """
    # Note: We don't properly parse `name` if it contains any "."s
    # like parso does at the moment. But it's mostly harmless to not
    # do so.
    #
    name_node = tree.Name(name, (0, 0), prefix=" "),

    if not alias:
        tail = name_node
    else:
        tail = tree.PythonNode("dotted_as_name", [name_node, tree.Keyword("as", (0, 0), prefix=" "), tree.Name(alias, (0, 0), prefix=" ")])

    return tree.ImportName(
        [
            tree.Keyword("import", (0, 0), prefix=prefix),
            tail,
        ],
    )


def make_import_from_namespace(namespace, alias=""):
    """Convert a dot-separated string to a parso object.

    if `namespace` has no dots, it imports using `import X`. If it does,
    it is `from X import Y`.

    Args:
        namespace (str): Something like "foo.bar.thing".

    Returns:
        :class:`parso.python.tree.ImportName` or :class:`parso.python.tree.PythonNode`:
            The created node.


    """
    if "." not in namespace:
        return make_import(namespace, alias=alias)

    base, tail = namespace.rsplit(".", 1)

    return make_from_import_using_parts(base, tail, alias=alias)


def make_name_node(namespace, prefix=None):

    def _add_dots_between_elements(nodes):
        children = []

        for element in nodes:
            children.append(element)
            children.append(tree.Operator(".", (0, 0)))

        children.pop()

        return children

    if "." not in namespace:
        return tree.Name(namespace, (0, 0), prefix=prefix)

    nodes = [tree.Name(name, (0, 0)) for name in namespace.split(".")]
    nodes[0].prefix = prefix
    children = _add_dots_between_elements(nodes)

    parent = tree.PythonNode("power", children)

    for child in parent.children:
        child.parent = parent

    return parent
