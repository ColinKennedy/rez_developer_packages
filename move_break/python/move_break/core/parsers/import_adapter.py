#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The main class used for a regular `import foo` Python import."""

import operator

from parso.python import tree
from parso_helper import node_seek

from . import base


class ImportAdapter(base.BaseAdapter):
    """The main class used for a regular `import foo` Python import."""

    @staticmethod
    def _get_namespaces(node):
        """Get the single dot-separated namespace for the given node.

        Args:
            node (:class:`parso.python.tree.ImportName`):
                A parso object that represents a Python import

        Returns:
            set[str]: A namespace like {"foo.bar"}.

        """
        return {_get_dotted_namespace(node)}

    @staticmethod
    def _replace(node, _, new_parts):
        """Change `node` to `new_parts`.

        Args:
            node (:class:`parso.python.tree.ImportName`):
                A parso object that represents a Python import.
            new_parts (list[str]):
                The namespace to replace `node` with. e.g. ["foo", "bar"].

        """
        for name_index, name in enumerate(node.get_defined_names()):
            parent = name.parent
            real_index = parent.children.index(name)
            parent.children[real_index].value = new_parts[name_index]

    @staticmethod
    def is_valid(node):
        """bool: Check if `node` is compatible with this class."""
        if not isinstance(node, tree.ImportName):
            return False

        for child in node_seek.iter_nested_children(node):
            if isinstance(child, tree.Operator) and child.value == ",":
                return False

        return True

    @staticmethod
    def get_import_type():
        """str: An identifier used to categorize instances of this class."""
        return "import"


def _get_dotted_namespace(node):
    """Convert a parso node into a human-readable Python namespace.

    Args:
        node (:class:`parso.python.tree.ImportName`):
            A parso node that represents a Python import.

    Returns:
        str: An importable Python namespace e.g. "foo.bar".

    """
    return ".".join(map(operator.attrgetter("value"), node.get_defined_names()))
