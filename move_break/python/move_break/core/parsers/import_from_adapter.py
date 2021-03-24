#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The main class used for a regular `from foo import bar` Python import."""

from __future__ import division

import operator

from parso.python import tree
from parso_helper import node_seek
from python_compatibility import iterbot

from .. import creator, import_helper, parsing_common, serializer
from . import base as base_


class ImportFromAdapter(base_.BaseAdapter):
    """The main class used for a regular `from foo import bar` Python import."""

    def _is_import_about_to_be_fully_replaced(self, old_namespace):
        known_namespaces = self._get_namespaces(self._node)

        if {old_namespace} == known_namespaces:
            return True

        if not self._partial:
            raise NotImplementedError("Need to write this case.")

        to_be_replaced = set()

        for namespace in known_namespaces:
            if namespace.startswith(old_namespace + "."):
                to_be_replaced.add(namespace)

        return to_be_replaced == known_namespaces

    @staticmethod
    def _get_namespaces(node):
        """Find every dot-separated namespace that this instance encapsulates.

        Args:
            node (:class:`parso.python.tree.ImportFrom`):
                Some node that may have one-or-more imports.

        Returns:
            set[str]: Dot-separated namespaces such as {"foo.bar.bazz", "foo.bar.thing"}.

        """
        namespaces = set()

        for path in node.get_paths():
            namespaces.add(".".join(map(operator.attrgetter("value"), path)))

        return namespaces

    def _get_known_tails(self, attributes):
        """Find every import from `attributes` that matches the namespaces of this instance.

        In this case, `attributes` could be like
        ["some.thing.blah.attribute"]. And this instance may contain an
        import such as `from some.thing import blah, more, things`.  And
        if that happens, {"blah"} is returned because that's the import
        name which would be used to refer to `attribute` in a module.

        Args:
            attributes (container[:class:`._Dotted`]):
                Each import namespace / attribute to check for.

        Returns:
            set[str]: Every found namespace, if any.

        """
        def _get_tail(namespace):
            return namespace.split(".")[-1]

        known_namespaces = self._get_namespaces(self._node)
        output = set()

        for namespace in known_namespaces:
            for attribute in attributes:
                if attribute.in_import_namespaces(namespace):
                    output.update(
                        _get_tail(namespace_)
                        for namespace_ in attribute.get_all_import_namespaces()
                    )

            output.add(_get_tail(namespace))

        return output

    def _kill_unneeded_imports(self, nodes, names):
        for node in nodes:
            if node.value not in names:
                continue

            _delete_name_and_extra_nodes(node)

    @staticmethod
    def _partially_replace_namespace(base_names, old_parts, new_parts, prefix):
        """Replace part (but not all) of a from-import.

        Args:
            base_names (iter[:class:`parso.python.tree.Name`]):
                The nodes that represent some Python import namespace.
            old_parts (iter[str]):
                Some tokens that should match with all or part of `names`,
                in the same order. This parameter is used to figure out if
                any part of `names` will be overwritten by other functions.
            new_parts (list[str]):
                The namespace to replace `node` with. e.g. ["foo", "bar"].
            prefix (str):
                Leading whitespace that will be added to the new import nodes.

        """
        start, end = import_helper.get_replacement_indices(base_names, old_parts)
        new_nodes = import_helper.make_replacement_nodes(new_parts, prefix)

        base_names[0].parent.children[start : end + 1] = new_nodes

    def _replace_tail(  # pylint: disable=too-many-arguments
        self, node, old_parts, new_parts, base_names, prefix
    ):
        """Replace the first half of a from-import and any part of the end, if possible.

        Args:
            node (:class:`parso.python.tree.ImportFrom`):
                A parso object that represents a Python from-import.
            old_parts (iter[str]):
                Some tokens that should match with all or part of `base_names`,
                in the same order. This parameter is used to figure out if
                any part of `base_names` will be overwritten by other functions.
            new_parts (list[str]):
                The namespace to replace `node` with. e.g. ["foo", "bar"].
            base_names (iter[:class:`parso.python.tree.Name`]):
                The nodes that represent some Python import namespace.
            prefix (str):
                Leading whitespace that will be added to the new import nodes.

        """
        old_namespaces = {old for old, _ in self._namespaces}

        if not _has_fully_described_namespace(
            self._get_namespaces(node), old_namespaces
        ):
            # We need to split the import statement in two
            children = _get_tail_children(node.children[3:])
            old_tail = old_parts[-1]
            children = [child for child in children if child.value == old_tail]
            _adjust_imported_names(".".join(new_parts), children)

            return

        # Replace "from foo.bar.thing import something"
        _fully_replace_base_and_tail(node, old_parts, new_parts, base_names, prefix, clear_alias=not self._aliases)

    # TODO : Replace this docstring and all of the others
    def _replace(
        self, node, old_parts, new_parts, namespaces=frozenset(), attributes=tuple()
    ):
        """Change `node` from `old_parts` to `new_parts`.

        Warning:
            This method directly modifies `node`.

        The logic of this function is a bit intense. It goes something like this.

        - If `old_parts` fully describes the "from foo.bar.thing" part of `node`
            - completely replace "foo.bar.thing" with whatever `new_parts` is.
        - If `old_parts` goes beyond "from foo.bar.thing" and actually
          starts touching the namespaces of "from foo.bar.thing import something".
            - replace both "foo.bar.thing" and "something" with the new namespace.
        - If `old_parts` only partiall describes `node`.
            - figure out what parts of "from foo.bar.thing" should be replaced or kept

        Args:
            node (:class:`parso.python.tree.ImportFrom`):
                A parso object that represents a Python import.
            old_parts (list[str]):
                The namespace that is expected to be all or part of the
                namespace that `node` defines.
            new_parts (list[str]):
                The namespace to replace `node` with. e.g. ["foo", "bar"].
            namespaces (iter[str]):
                Reference (not full) attribute namespaces. e.g. `["module.attribute"]`
                These namespaces indicate what is "in-use" in the
                current graph, post refactoring. If an import statements
                imports multiple statements but at least one of its
                imports also is present in `namespaces` then the import
                is split into a separate import statement, to retain the
                original behavior.
            attributes (container[:class:`._Dotted`], optional):
                Each import namespace / attribute to check for. These
                attributes are the ones which previously existed in
                modules, **prior** to any replacing / refactoring.

        """
        # TODO : Consider replacing the the parent, instead of directly
        # modifying the current node
        #
        base_names = _get_base_names(node.children[1])
        prefix = base_names[0].prefix
        old_attributes = [old_ for old_, _ in attributes]

        known_tails = self._get_known_tails(old_attributes)
        used_tails = {tail for tail in known_tails if _is_used(tail, namespaces)}

        is_still_needed = _is_needed(node, namespaces)

        if not _is_multi_import(node):
            if is_still_needed:
                old_namespace = ".".join(old_parts)

                if not self._is_import_about_to_be_fully_replaced(old_namespace):
                    # Don't mess with this import because messing with
                    # it would cause the import to completely break.
                    #
                    return

                known_namespaces = self._get_namespaces(self._node)
                inner_imports = parsing_common.get_inner_imports(known_namespaces, attributes, partial=self._partial)

                for old_parts_, new_parts_ in inner_imports:
                    _fully_replace_base_and_tail(
                        node, old_parts_, new_parts_, base_names, prefix, clear_alias=not self._aliases,
                    )

                if not self._partial:
                    return

                # TODO : Finish this bit
                # raise ValueError('STOP')
                # # Replace the entire "from foo.bar.thing import something" import
                # new_nodes = import_helper.make_replacement_nodes(new_parts, prefix, parent=node)
                # _fully_replace_base(base_names, new_nodes)

                return

        if is_still_needed:
            index = _get_import_index(node)
            tails_to_delete = _get_tails_to_delete(
                known_tails - used_tails,
                old_attributes,
                namespaces,
            )
            after_the_import = node.children[index + 1:]
            children = _get_tail_children(after_the_import)

            self._kill_unneeded_imports(children, tails_to_delete)

            return

        if self._partial and _old_parts_equals_base(base_names, old_parts):
            # Replace "from foo.bar.thing"
            new_nodes = import_helper.make_replacement_nodes(new_parts, prefix)
            _fully_replace_base(base_names, new_nodes)

            return

        if _old_parts_exceeds_base(base_names, old_parts):
            self._replace_tail(node, old_parts, new_parts, base_names, prefix)

            return

        if not self._partial:
            return

        self._partially_replace_namespace(base_names, old_parts, new_parts, prefix)

    @staticmethod
    def is_valid(node):
        """Check if `node` is compatible with this class.

        Args:
            node (:class:`parso.python.tree.ImportFrom`):
                A parso node. Any unrecognized type will return False.

        Returns:
            bool: If `node` is the right type.

        """
        return isinstance(node, tree.ImportFrom)

    @staticmethod
    def get_import_type():
        """str: An identifier used to categorize instances of this class."""
        return "import_from"

    def get_node_namespace_mappings(self):
        """Get each "real" namespace and its "aliased" counterpart.

        If the namespace has no alias then the key / value pair will
        both point to the "real" namespace.

        Returns:
            dict[str, str]: Every unique, full import namespace.

        """
        aliases = {
            name: alias
            for name, alias in self._node._as_name_tuples()  # pylint: disable=protected-access
            if alias is not None
        }

        output = dict()

        for paths in self._node.get_paths():
            tail = paths[-1]
            aliased_or_paths = paths[:-1] + [aliases.get(tail, paths[-1])]

            output[serializer.to_dot_namespace(paths)] = serializer.to_dot_namespace(
                aliased_or_paths
            )

        return output

    def __contains__(self, namespace):
        """Check if this instance defines a given Python dot-separated namespace.

        If the node stored in this instance is a star import like "from
        foo import *" then even if `namespace` only matches the base
        (non-star) part then this method will return True.

        Args:
            namespace (str): A Python dot-separated import string. Such as "foo.bar".

        Returns:
            bool: If this instance contains `namespace`.

        """
        if super(ImportFromAdapter, self).__contains__(namespace):
            return True

        if not self._node.is_star_import():
            return False

        # Get the namespace but without the "*" at the end
        base_namespace = ".".join(namespace.split(".")[:-1])

        return base_namespace in self._get_namespaces(self._node)


def _has_comma(node):
    """bool: Check if `node` or some child within `node` is a comma."""
    for child in node_seek.iter_nested_children(node):
        if _is_comma(child):
            return True

    return False


def _has_fully_described_namespace(required_namespaces, user_provided_namespaces):
    """Check if every namespace that needs to exist is in another list of namespaces.

    If the user is doing a non-partial replacement, that means every namespace
    that the from-import adds must have some old / new pair to be replaced with.

    Args:
        required_namespaces (iter[str]):
            The Python dot-separated namespaces that must exist. These
            namspaces should be every import that from a from-import.
            e.g. "from foo import bar, bazz", this would be
            {"foo.bar", "foo.bazz"}.
        user_provided_namespaces (set[str]):
            The Python dot-separated namespaces that a person should
            have provided to the :class:`ImportFromAdapter`.

    Returns:
        bool: If every namespace in `required_namespaces` is in `user_provided_namespaces`.

    """
    for namespace in required_namespaces:
        if namespace not in user_provided_namespaces:
            return False

    return True


def _is_alias(node):
    return isinstance(node, tree.Keyword) and node.value == "as"


def _is_alias_name(node):
    """Check if a parso node is actually defining an alias, and not a import namespace.

    Args:
        node (:class:`parso.python.tree.Name`):
            Some parso node that (presumably) is part of an import statement.

    Returns:
        bool: If `node` defines a user-provided name, not an actual Python namespace.

    """
    parent = node.parent
    index = parent.children.index(node)
    siblings = parent.children[:index]

    if not siblings:
        return False

    keyword = siblings[-1]

    return _is_alias(keyword)


def _is_comma(node):
    return isinstance(node, tree.Operator) and node.value == ","


def _is_import(node):
    return isinstance(node, tree.Keyword) and node.value == "import"


def _is_multi_import(node):
    index = _get_import_index(node)

    if index == -1:
        return False

    after_the_import = node.children[index + 1:]

    for child in after_the_import:
        if _is_comma(child):
            return True

        for inner in node_seek.iter_nested_children(child):
            if _is_comma(inner):
                return True

    return False


def _is_needed(node, namespaces):
    real_tails = tuple(tail.value + "." for tail in node.get_defined_names())

    for namespace in namespaces:
        if namespace.startswith(real_tails):
            return True

    return False


def _is_used(name, candidates):
    name = name.rstrip(".") + "."

    for candidate in candidates:
        if candidate.startswith(name):
            return True

    return False


def _delete_name_and_extra_nodes(node):
    def _get_non_aliased_names(nodes):
        names = []

        for index, node in enumerate(nodes):
            if not isinstance(node, tree.Name):
                continue
            elif index == 0:
                names.append(node)
            elif not _is_alias(nodes[index - 1]):
                names.append(node)

        return names

    parent = node.parent

    if isinstance(parent, tree.PythonNode) and parent.type in {"import_as_name", "import_as_names"} and len(_get_non_aliased_names(parent.children)) == 1:
        # Clean up the parent
        index = parent.parent.children.index(parent)

        _delete_node_and_alias_plus_comma(index, parent.parent.children)

        # If cleaning the parent would leave the import in a broken
        # state then clean up the grandparent, too.
        #
        end = parent.parent.children[-1]

        if _is_import(end):
            super_parent = parent.parent.parent
            index = super_parent.children.index(parent.parent)

            del super_parent.children[index]

        return

    children = node.parent.children
    index = children.index(node)

    _delete_node_and_alias_plus_comma(index, children)


def _delete_node_and_alias_plus_comma(index, children):
    """Cleanly remove `index` from `children` and clean up any remaining commas.

    If you have an import like `from X import Y as Z, A` and you want
    to remove the Y-th index, the result would look like `from X import
    A` by the end. And if you remove the A-th index, it becomes `from X
    import Y`.

    Basically, no matter what you throw at this function, it'll give you
    a clean result.

    Args:
        index (int):
            A 0-or-greater value of the element to remove from `children`.
        children (container[:class:`parso.python.tree.PythonNode`]):
            Some nodes to / remove. It's assumed are the `Y as Z, A`
            part of a `from X import Y as Z, A` import.

    """
    def _kill_leading_comma_if_needed(index, children):
        if index == 0:
            return

        if _is_comma(children[index - 1]):
            del children[index - 1]

    del children[index]

    try:
        next_node = children[index]
    except IndexError:
        _kill_leading_comma_if_needed(index, children)

        return

    if _is_comma(next_node):
        del children[index]  # Delete the comma

        return

    if _is_alias(next_node):
        del children[index]  # Delete the alias

        if index < len(children):
            del children[index]  # Delete the comma


def _fully_replace_base_and_tail(node, old_parts, new_parts, base_names, prefix, clear_alias=False):
    new_nodes = import_helper.make_replacement_nodes(new_parts[:-1], prefix, parent=node)
    _fully_replace_base(base_names, new_nodes)
    children = _get_tail_children(node.children[3:])
    _maybe_replace_imported_names(old_parts[-1], new_parts[-1], children, clear_alias=clear_alias)


def _fully_replace_base(base_names, nodes):
    """Replace ever node in `base_names` with a new Python namespace.

    Args:
        base_names (list[:class:`parso.python.tree.Name`]):
            The tokens (in parso form) of a Python import namespace. But
            without the dots.
        nodes (list[:class:`parso.python.tree.Name` or :class:`parso.python.tree.Operator`]):
            The converted nodes of `parts`.

    """
    parent = base_names[0].parent

    indices = {parent.children.index(child) for child in base_names}
    start = min(indices)
    end = max(indices)

    parent.children[start : end + 1] = nodes


def _maybe_replace_imported_names(old, new, nodes, clear_alias=False):
    """Replace every node in `nodes` with `new`, if its text is `old`.

    Args:
        old (str):
            The name of an import namespace that may be inside `nodes`.
        new (str):
            The namespace to replace `old` with, if it exists.
        nodes (iter[:parso.python.tree.Name`]):
            The ends of a from-import to potentially replace.
            e.g. with an import like "from foo import bar, thing",
            this would be [tree.Name("bar"), tree.Name("thing")].

    """

    def _is_keyword_and_name(nodes):
        if len(nodes) < 2:
            return False

        if not _is_alias(nodes[0]):
            return False

        return isinstance(nodes[1], tree.Name)

    def _get_inner_children(node):
        children = []

        for child in node_seek.iter_nested_children(node):
            if not _is_alias_name(child):
                children.append(child)

        return children

    for current_ending_node in nodes:
        if isinstance(current_ending_node, tree.Name):
            if current_ending_node.value == old:
                current_ending_node.value = new

            if clear_alias:
                children = current_ending_node.parent.children
                index = children.index(current_ending_node)
                next_children = children[index + 1:]

                if _is_keyword_and_name(next_children):
                    children[index + 1: index + 3] = []

                if len(children) == 1 and isinstance(children[0], tree.Name):
                    parent = current_ending_node.parent
                    grand_parent = current_ending_node.parent.parent
                    index = grand_parent.children.index(parent)
                    grand_parent.children[index] = children[0]

                    _remove_parentheses_around_name(grand_parent.children[index])


            continue

        children = _get_inner_children(current_ending_node)

        for node in children:
            if node.value == old:
                node.value = new


def _get_base_names(base):
    """Get every token of a Python import, as parso nodes.

    Args:
        base (:class:`parso.python.tree.Name` or :class:`parso.python.tree.PythonNode`):
            Either a full Python namespace import or a part of one.

    Returns:
        list[:class:`parso.python.tree.Name`]:
            Find every token that is part of a Python import.

    """
    if hasattr(base, "children"):
        base_children = base.children
    else:
        base_children = [base]

    return [name for name in base_children if isinstance(name, tree.Name)]


def _get_import_index(node):
    for index, child in enumerate(node.children):
        if _is_import(child):
            return index

    return -1


def _get_parents_up_to_import_from(node):
    # """Get the :class:`parso.python.tree.ImportFrom` parent of `node`."""
    previous = None
    parents = []

    while previous != node:
        if isinstance(node, tree.ImportFrom):
            return parents

        previous = node
        node = node.parent
        parents.append(node)

    return parents


def _get_tails_to_delete(tails_to_consider, attributes, namespaces):
    tails = set()

    for tail in tails_to_consider:
        match = False

        for attribute in attributes:
            heads = tuple(reference.split(".")[0] for reference in attribute.get_import_references())

            if tail not in heads:
                continue

            match = True
            heads = tuple(head + "." for head in heads)

            for namespace in namespaces:
                if namespace.startswith(heads):
                    break
            else:
                tails.add(tail)

        if not match:
            tails.add(tail)

    return tails


def _get_tail_children(nodes):
    """Get the tail namespaces of a from-import.

    In other words, from "from foo import bar, thing", get the "bar" and "thing".

    Args:
        nodes (iter[:class:`parso.python.tree.PythonBaseNode`]):
            All parso objects that represent a Python from-import's
            tail. It may contain commas and other syntax-specific parts.
            But this will all be filtered out before being returned.

    Returns:
        list[:class:`parso.python.tree.PythonBaseNode`]: The found tail nodes.

    """
    children = []

    for node in nodes:
        if isinstance(node, tree.Name):
            children.append(node)
        else:
            for child in node_seek.iter_nested_children(node):
                if isinstance(child, tree.Name) and not _is_alias_name(child):
                    children.append(child)

    return children


def _old_parts_equals_base(base_names, parts):
    """Check if `parts` describes the given parso nodes exactly and nothing more.

    Most of the time, `parts` will describe all of `base_names` plus
    some extra Python namespace. In those situations, this function
    returns False. It only returns true if it matches exactly (with no
    extra namespace data).

    Args:
        base_names (list[:class:`parso.python.tree.Name`]):
            The parso nodes that represent a Python import (but with no "."s).

    Returns:
        bool: If `parts` is the same as `base_names`.

    """
    base_namespace = [name.value for name in base_names]

    return base_namespace == parts


def _old_parts_exceeds_base(base_names, parts):
    """Check if `parts` describes all of `base_names` plus extra data.

    Args:
        base_names (list[:class:`parso.python.tree.Name`]):
            The parso nodes that represent a Python import (but with no "."s).

    Returns:
        bool: If `parts` is includes all of `base_names` + more data.

    """
    base_namespace = [name.value for name in base_names]

    return base_namespace == parts[:-1]


def _remove_node_and_comma(node):
    """Delete a sibling comma, assuming that `node` comes from a from-import.

    Args:
        node (:class:`parso.python.tree.Name`): Some part of a Python from-import.

    Raises:
        RuntimeError: If `node` is not a multi-comma import.

    """

    def _get_alias(node):
        parent = node.parent

        if not isinstance(parent, tree.PythonNode):
            return None

        if not any(node for node in parent.children if _is_alias(node)):
            return None

        return parent.children[-1]

    def _remove_trailing_node(node):
        if _is_comma(node):
            del node.parent.children[-1]

    parents = _get_parents_up_to_import_from(node)

    if len(parents) == 1:
        # This only happens when you have a `from X import Y` import If
        # you have `from X import Y as Z, etc` then the number of parents
        # is greater than 1.
        #
        return None

    parent = _get_parents_up_to_import_from(node)[-2]

    try:
        next(index_ for index_, node_ in enumerate(parent.children) if _is_comma(node_))
    except StopIteration:
        raise RuntimeError(
            'Node "{parent}" has no commas. This function is meant '
            'to split a multi-comma import.'.format(
                parent=parent
            )
        )

    alias = _get_alias(node)

    try:
        index = parent.children.index(node)
    except ValueError:
        index = 0

    if index + 1 > len(parent.children):
        # We're at the end of a sequence of imports e.g. "from foo import bar, bazz, another"
        del parent.children[index - 1]  # Delete the previous ","
        del parent.children[index - 1]  # Now delete the name

        return alias

    # We must be at the beginning or somewhere in the middle of the import.
    del parent.children[index]  # Remove the name

    if index == len(parent.children):
        # We've removed the last import in an multi-import
        # e.g. Removing "fizz" from `from foo import bar, fizz`
        #
        # To prevent `from foo import bar,` - remove the trailing `,`
        #
        _remove_trailing_node(parent.children[-1])

        return alias

    if not parent.children:
        return alias

    commas = [
        index_ for index_, node_ in enumerate(parent.children) if _is_comma(node_)
    ]
    comma_occurrence_index = index // 2
    real_comma_index = commas[comma_occurrence_index]

    del parent.children[real_comma_index]

    return alias


def _remove_parentheses_around_name(node):
    if len(node.parent.children) != 1:
        return

    children = node.parent.parent.children
    end = children[-1]

    if isinstance(end, tree.Operator) and end.value == ")":
        open_parentheses = children[-3]
        # Delete the "("
        del children[-3]

        # Make sure that `node` has whitespace, for sure, or it can
        # cause imports to break.
        #
        node.prefix = node.prefix or open_parentheses.prefix

        # Delete the ")"
        del children[-1]


def _still_has_used_namespace(names, used_namespaces):
    """Check if any `names` are found within `used_namespaces`.

    It's assumed that `names` is the "end" of an attribute namespace and
    `used_namespaces` are attribute namespaces.

    Args:
        names (iter[str]):
            Root attribute namespaces. e.g. `["module"]`
        used_namespaces (iter[str]):
            Full attribute namespaces. e.g. `["module.attribute"]`

    Returns:
        bool:
            If `names` and `used_namespaces` have anything in common,
            return True. Otherwise, return False.

    """
    dot_names = tuple(name + "." for name in names if name)

    for namespace in used_namespaces:
        if namespace.startswith(dot_names):
            return True

    return False


def _adjust_imported_names(new_namespace, nodes):
    """Split a from-import into 2 separate import statements.

    Args:
        new_namespace (str):
            The items to use for a new import e.g. "foo.bar".
        nodes (iter[:class:`parso.python.tree.Name`]):
            The tail of a from-import whose import namespaces will be split.

    """

    def _adjust_prefix(node):
        """Put `node` on its own line but retain its original leading indent."""
        prefix_node = node_seek.get_node_with_first_prefix(node)
        original = prefix_node.prefix
        prefix_node.prefix = "\n{original}".format(original=original)

        return original

    def _add_new_import(import_from, new_namespace, alias=""):
        """Add a new from-import of `new_namespace` as a sibling of `node`."""
        parent = import_from.parent
        index = parent.children.index(import_from)

        prefix = _adjust_prefix(import_from)
        new_import_node = creator.make_import_from_namespace(new_namespace, prefix=prefix, alias=alias)

        parent.children.insert(index, new_import_node)

    for current_ending_node in nodes:
        parents = _get_parents_up_to_import_from(current_ending_node)

        if not parents:
            raise RuntimeError(
                'Node "{current_ending_node}" has no parents.'.format(
                    current_ending_node=current_ending_node
                )
            )

        if len(parents) < 2:
            raise RuntimeError(
                'Node "{current_ending_node.parent}" has no commas. This function is meant '
                'to split a multi-comma import.'.format(
                    current_ending_node=current_ending_node
                )
            )

        top_parent = parents[-1]
        closest_parent = parents[-2]

        if not [
            index_
            for index_, node_ in enumerate(closest_parent.children)
            if _is_comma(node_)
        ]:
            raise RuntimeError(
                'Node "{closest_parent}" has no commas. This function is meant '
                'to split a multi-comma import.'.format(
                    closest_parent=closest_parent
                )
            )

        alias = _remove_node_and_comma(current_ending_node)

        if alias:
            alias = alias.value
        else:
            alias = ""

        _add_new_import(top_parent, new_namespace, alias=alias)

        return
