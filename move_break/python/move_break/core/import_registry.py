#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""A module that finds how to parse imports from another Python module."""

from .parsers import import_adapter, import_from_adapter, import_name_adapter


_OPTIONS = (
    import_from_adapter.ImportFromAdapter,
    import_name_adapter.ImportNameAdapter,
    import_adapter.ImportAdapter,
)


def get_import_data(node, partial=False, namespaces=frozenset(), aliases=False):
    """Get the correct class needed to process `node`.

    Args:
        node (
            :class:`parso.python.tree.Import`
            or :class:`parso.python.tree.ImportName`,
            or :class:`parso.python.tree.ImportFrom`,
        ):
            The import node that must be parsed.
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
        :class:`.BaseAdapter` or NoneType:
            An adapter instance or nothing, if no adapter could be found.

    """
    for option in _OPTIONS:
        if option.is_valid(node):
            return option(node, partial=partial, namespaces=namespaces, aliases=aliases)

    return None


def get_plugin_types():
    """set[str]: Get the IDs for each import-replacer class."""
    return set(option.get_import_type() for option in _OPTIONS)
