#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The main "worker" module for the command-line `move_break` tool."""

import itertools

import parso

from .core import parser


def _get_graph(path):
    """:class:`parso.python.tree.Module`: Convert a file path into a parso graph."""
    with open(path, "r") as handler:
        code = handler.read()

    return parso.parse(code)


def run(files, namespaces, partial=False):
    """Replace the imports of every given file.

    Not every path in `files` will actually be overwritten. Because
    that depends on whether the file includes a namespace import from
    `namespaces`.

    Args:
        files (iter[str]):
            The absolute path to Python files to change.
        namespaces (iter[tuple[str, str]]):
            Python dot-separated namespaces that need to be changed.
            Each tuple is the existing namespace and the namespace that
            should replace it.
        partial (bool, optional):
            If True and an import found in `files` is not fully
            described by the user-provided `namespaces`, replace
            the import anyway. Otherwise, the entire import most be
            discoverable before the import is replaced. Default is False.

    Returns:
        set[str]: The paths from `files` that were actually overwritten.

    """
    output = set()

    for path in files:
        changed = False
        graph = _get_graph(path)
        imports = parser.get_imports(graph, partial=partial, namespaces=namespaces)

        for statement, (old, new) in itertools.product(imports, namespaces):
            if old in statement:
                statement.replace(old, new)
                changed = True

        if changed:
            with open(path, "w") as handler:
                handler.write(graph.get_code())

            output.add(path)

    return output
