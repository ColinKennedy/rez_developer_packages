#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The main "worker" module for the command-line `move_break` tool."""

import itertools
import logging
import re

from . import finder
from .core import attribute_handler, parser

_IMPORT_EXPRESSION = re.compile("^import:(?P<namespace>[\w\.]+)$")
_LOGGER = logging.getLogger(__name__)


def _get_import_match(text):
    match = _IMPORT_EXPRESSION.match(text)

    if not match:
        return ""

    return match.group("namespace")


def _process_namespaces(namespaces):
    output = []
    explicits = set()
    unknowns = []
    attributes = []

    for old, new in namespaces:
        old_match = _get_import_match(old)
        new_match = _get_import_match(new)

        if old_match or new_match:
            explicits.add(old_match)
            output.append((old_match, new_match))

            continue

        unknowns.append((old, new))

    for old, new in unknowns:
        for explicit in explicits:
            if old.startswith(explicit):
                attributes.append((old, new))

                break
        else:
            output.append((old, new))

    return output, attributes


def move_imports(  # pylint: disable=too-many-arguments
    files,
    namespaces,
    partial=False,
    import_types=frozenset(),
    aliases=False,
    continue_on_syntax_error=False,
):
    """Replace the imports of every given file.

    Not every path in `files` will actually be overwritten. Because
    that depends on whether the file includes a namespace import from
    `namespaces`.

    Args:
        files (iter[str]):
            The absolute path to Python files to change.
        namespaces (list[tuple[str, str]]):
            Python dot-separated namespaces that need to be changed.
            Each tuple is the existing namespace and the namespace that
            should replace it.
        partial (bool, optional):
            If True and an import found in `files` is not fully
            described by the user-provided `namespaces`, replace
            the import anyway. Otherwise, the entire import most be
            discoverable before the import is replaced. Default is False.
        import_types (set[str], optional):
            If this is non-empty, only import adapters whose type
            match the names given here will be processed.
            Default: set().
        aliases (bool, optional):
            If True and replacing a namespace would cause Python
            statements to fail, auto-add an import alias to ensure
            backwards compatibility If False, don't add aliases. Default
            is False.
        continue_on_syntax_error (bool, optional):
            If True and a path in `files` is an invalid Python module
            and otherwise cannot be parsed then skip the file and keep
            going. Otherwise, raise an exception. Default is False.

    Raises:
        RuntimeError:
            If `continue_on_syntax_error` is False and a file with a
            syntax error is found.
        ValueError:
            If `namespaces` is empty or if any pair in `namespaces` has
            the same first and second index.

    Returns:
        set[str]: The paths from `files` that were actually overwritten.

    """
    output = set()

    if not namespaces:
        raise ValueError("Namespaces cannot be empty.")

    for old, new in namespaces:
        if old == new:
            raise ValueError(
                'Pair "{old}/{new}" cannot be the same.'.format(old=old, new=new)
            )

    namespaces, attributes = _process_namespaces(namespaces)

    for path in files:
        changed = False

        try:
            graph = finder.get_graph(path)
        except RuntimeError:
            _LOGGER.warning('Couldn\'t parse "%s" as a Python file.', path)

            if not continue_on_syntax_error:
                raise

            continue

        imports = parser.get_imports(
            graph, partial=partial, namespaces=namespaces, aliases=aliases
        )

        for statement, (old, new) in itertools.product(imports, namespaces):
            if import_types and statement.get_import_type() not in import_types:
                continue

            if old in statement:
                statement.replace(old, new)
                changed = True

        new_imports = parser.get_imports(
            graph, partial=partial, namespaces=namespaces, aliases=aliases
        )

        changed_attributes = []

        if partial or attributes:
            changed_attributes = attribute_handler.replace(
                attributes,
                graph,
                namespaces,
            )

        if changed_attributes:
            attribute_handler.add_imports([new for _, new in changed_attributes], graph)

            changed = True

        if changed:
            with open(path, "w") as handler:
                handler.write(graph.get_code())

            output.add(path)

    return output
