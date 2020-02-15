#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The main module that gets import statements in a form that's easy to query and overwrite."""

from parso_helper import node_seek

from . import import_registry


def get_imports(graph, partial=False, namespaces=frozenset(), aliases=False):
    """Find every import in `graph`.

    Args:
        graph (:class:`parso.python.tree.Module`):
            Some parso node that may have Python imports iside of it.
        partial (bool, optional):
            If True, allow namespace replacement even if the user
            doesn't provide 100% of the namespace. If False, they must
            describe the entire import namespace before it can be
            renamed. Default is False.
        namespaces (set[str], optional):
            If `partial` is False, these dot-separated Python import
            namespaces are used to figure out if it's okay to replace an
            import or if any part of an import statement is missing. If
            no namespaces are given then `partial` must be set to True.
            Default: set().
        aliases (bool, optional):
            If True and replacing a namespace would cause Python
            statements to fail, auto-add an import alias to ensure
            backwards compatibility If False, don't add aliases. Default
            is False.

    Returns:
        :class:`.BaseAdapter`:
            Every import in `graph`, returned as a class that can easily
            query its data or replace it.

    """
    imports = set()
    processed = set()  # This variable makes sure nodes are only ever parsed once

    # We reverse the nested children because parso nests its nodes
    # in ways that makes it hard to choose the correct adapter class
    # without starting from the bottom-level nodes and working our way
    # up each node's list of parents.
    #
    for child in reversed(list(node_seek.iter_nested_children(graph))):
        parents = node_seek.iter_parents(child)

        if any(parent for parent in parents if parent in processed):
            # Make sure that if a parent of `child` was parsed to not try to parse `child`
            continue

        adapter = import_registry.get_import_data(
            child,
            partial=partial,
            namespaces=namespaces,
            aliases=aliases,
        )

        if adapter:
            imports.add(adapter)

        processed.add(child)

    return imports
