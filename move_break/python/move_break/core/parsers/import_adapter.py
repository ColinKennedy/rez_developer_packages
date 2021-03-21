#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The main class used for a regular `import foo` Python import."""

import operator

from parso.python import tree
from parso_helper import node_seek

from .. import creator, serializer
from . import base as base_


class ImportAdapter(base_.BaseAdapter):
    """The main class used for a regular `import foo` Python import.

    This also covers `import foo as bar`

    If you're looking for `import foo, bazz, bazz`, see
    :mod:`.import_name_adapter`.

    """

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
    def _get_known_heads(attributes):
        heads = set()

        for attribute in attributes:
            heads.update(attribute.get_all_import_namespaces())

        return heads

    def _replace(self, node, old_parts, new_parts, namespaces=frozenset(), attributes=tuple()):
        """Change `node` to `new_parts`.

        Args:
            node (:class:`parso.python.tree.ImportName`):
                A parso object that represents a Python import.
            new_parts (list[str]):
                The namespace to replace `node` with. e.g. ["foo", "bar"].
            namespaces (iter[str]):
                Reference (not full) attribute namespaces. e.g.
                `["module.attribute"]` These namespaces indicate what
                is "in-use" in the current graph, post refactoring. If
                an import statements imports multiple statements but at
                least one of its imports also is present in `namespaces`
                then the import is split into a separate import
                statement, to retain the original behavior.
            attributes (container[:class:`._Dotted`], optional):
                Each import namespace / attribute to check for. These
                attributes are the ones which previously existed in
                modules, **prior** to any replacing / refactoring.

        """
        known_heads = self._get_known_heads(attributes)

        for namespace in namespaces:
            head = namespace.split(".")[0]

            if head in known_heads and not self._aliases:
                return

        if len(new_parts) > 1:
            # If we're expanding `import foo` to `from blah import thing`, do it
            base = new_parts[:-1]
            tail = new_parts[-1]
            prefix_node = node_seek.get_node_with_first_prefix(node)
            index = node.parent.children.index(node)
            new_node = creator.make_from_import_using_parts(
                ".".join(base), tail, prefix=prefix_node.prefix,
            )
            node.parent.children[index] = new_node

            return

        # TODO : Consider changing this to replace the parent index,
        # instead of modify the existing node
        #
        for name_index, name in enumerate(_iter_namespace_names(node)):
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

    def get_node_namespace_mappings(self):
        """Get each "real" namespace and its "aliased" counterpart.

        If the namespace has no alias then the key / value pair will
        both point to the "real" namespace.

        Returns:
            dict[str, str]: The unique, found for this import namespaces.

        """
        output = dict()

        for (
            path,
            alias,
        ) in self._node._dotted_as_names():  # pylint: disable=protected-access
            name = path[0]
            name = serializer.to_dot_namespace([name])

            if alias:
                output[name] = serializer.to_dot_namespace([alias])
            else:
                output[name] = name

        return output


def _get_dotted_namespace(node):
    """Convert a parso node into a human-readable Python namespace.

    Args:
        node (:class:`parso.python.tree.ImportName`):
            A parso node that represents a Python import.

    Returns:
        str: An importable Python namespace e.g. "foo.bar".

    """
    return ".".join(
        map(operator.attrgetter("value"), _iter_namespace_names(node))
    )


def _iter_namespace_names(node):
    for path, _ in node._dotted_as_names():
        yield path[0]
