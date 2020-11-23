#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The main class used to modify a Rez package's `requires` attribute."""

import collections
import copy
import itertools

from parso.python import tree
from parso_helper import node_seek
from rez import package_serialise
from rez.vendor.schema import schema
from rez.vendor.version import requirement as rez_requirement
from rez.vendor.version import version as rez_version

from .. import convention, parso_utility
from . import base

_DEFAULT_PREFIX = "    "


class RequiresAdapter(base.BaseAdapter):
    """The main class used to modify a Rez package's `requires` attribute."""

    @staticmethod
    def check_if_invalid(data):
        """str: If `data` is invalid, return a message explaining why."""
        try:
            package_serialise.package_serialise_schema.validate(
                {
                    "name": "",  # This key is required so we just give it nothing
                    "requires": data,
                }
            )
        except schema.SchemaError as error:
            return str(error)

        return ""

    @staticmethod
    def modify_with_existing(graph, data, append=False):
        """Add `data` to a parso node `graph`.

        Args:
            graph (:class:`parso.python.tree.Module`):
                Some node that will either be appended to or have some
                of its contents overwritten and returned.
            data (list[str]):
                Rez requirements to convert to parso nodes and added to `graph`.
            append (bool, optional):
                If False and `graph` contains an existing version for a
                Rez package which conflicts with `data`, that version
                conflict is resolved as best as possible. If True,
                `data` is forced onto `graph`, without considering
                existing package requirements. Default is False.

        Returns:
            str:
                The modified Python source code. It should resemble the
                source code of `graph` plus any serialized `data`.

        """
        try:
            assignment = parso_utility.find_assignment_nodes("requires", graph)[-1]
        except IndexError:
            assignment = None

        existing_data = _get_entries(assignment)
        prefix = _get_prefix(assignment) or _DEFAULT_PREFIX

        if not append:
            data = _resolve_data_conflicts(
                data, [_node_to_requirement(node) for node in existing_data],
            )

        data_nodes = _make_nodes(data, prefix=prefix)
        final_data = _merge_list_entries(existing_data, data_nodes)
        node = _make_new_list(final_data)
        graph = convention.insert_or_append(node, graph, assignment, "requires")

        return graph.get_code()

    @staticmethod
    def remove_from_attribute(graph, data):
        """Delete `data` from `graph`, if it exists.

        Args:
            graph (:class:`parso.python.tree.Module`):
                The parso node that will contains a "requires" attribute
                that this function will modify.
            data (list[str]):
                The requirements that may exist in `graph` and will be elimnated.

        Returns:
            str: The original `graph` but as a result of the deleted content.

        """
        try:
            assignment = parso_utility.find_assignment_nodes("requires", graph)[-1]
        except IndexError:
            # If this happens, it just means that there's nothing to remove
            return graph.get_code()

        existing_data = _get_entries(assignment)
        prefix = _get_prefix(assignment) or _DEFAULT_PREFIX

        data_nodes = _make_nodes(data, prefix=prefix)
        final_data = _remove_existing_entries(existing_data, data_nodes)

        node = _make_new_list(final_data)
        graph = convention.insert_or_append(node, graph, assignment, "requires")

        return graph.get_code()

    @staticmethod
    def supports_appending():
        """bool: Allow force-replacing a package family's required package version if True."""
        return True


def _is_list_root_definition(node):
    """bool: If `node` defines the inner part of a list of "help" entries."""
    return isinstance(node, tree.PythonNode) and node.type == "testlist_comp"


def _get_entries(node):
    """Get the existing "requires" assignment parso nodes.

    Args:
        node (:class:`parso.python.tree.ExprStmt`):
            A parso assignment node that defines "requires".
            e.g. Imagine "requires = ["foo-1"]", but as a single Python node.

    Returns:
        list[:class:`parso.python.tree.String`]: The existing requirements in `node`.

    """
    root_entries = _get_inner_list_entries(node)

    if not root_entries:
        return []

    entries = []

    for item in root_entries:
        for child in node_seek.iter_nested_children(item):
            if not isinstance(child, tree.Operator):
                entries.append(child)

    return entries


def _get_inner_list_entries(node):
    """Find the literal "requires" entries of a node.

    Args:
        node (:class:`parso.python.tree.PythonBaseNode`):
            A parso object that (we assume) has 0+ child list parso
            objects. Each child found is returned.

    Returns:
        list[:class:`parso.python.tree.PythonNode`]:
            The found key / value "requires" attribute entries, if any.

    """
    entries = []

    for child in node_seek.iter_nested_children(node):
        if not _is_list_root_definition(child):
            continue

        if any(
            child_ for child_ in child.children if isinstance(child_, tree.PythonNode)
        ):
            continue

        entries.append(child)

    return entries


def _get_prefix(node):
    """Find the indentation used by `node`.

    This function ignores newlines and just gets the spaces / tabs used.

    Args:
        node (:class:`parso.python.tree.PythonBaseNode`):
            A parso object that is assumed to define a "requires" attribute.

    Returns:
        str: The leading indentation found, if any.

    """
    prefixes = set()

    for child in _get_inner_list_entries(node):
        prefix_node = node_seek.get_node_with_first_prefix(child)
        prefixes.add(prefix_node.prefix)

    counter = collections.Counter(prefixes)

    try:
        common = counter.most_common(1)[0]

        return common[0].strip("\n")
    except IndexError:
        return ""


def _escape(text):
    """str: Remove double-quotes around text."""
    return text.strip('"').strip("'")


def _make_new_list(requirements):
    """Make a flat Python list, using parso nodes.

    Args:
        requirements (iter[:class:`parso.python.tree.String`]):
            The Rez requirements that'll be used to generate the new
            list. No nodes related to punctuation should be used here.
            Just requirements.

    Returns:
        :class:`parso.python.tree.PythonNode`: The generated list.

    """
    nodes = []

    for requirement in requirements:
        nodes.append(requirement)
        nodes.append(tree.Operator(",", (0, 0)))

    prefix = "\n"

    if not nodes:
        prefix = ""

    return tree.PythonNode(
        "atom",
        [tree.Operator("[", (0, 0))]
        + nodes
        + [tree.Operator("]", (0, 0), prefix=prefix)],
    )


def _make_nodes(data, prefix=""):
    """Make basic parso nodes to describe `data`.

    Args:
        data (iter[str]): Some Rez requirement objects to convert into parso nodes.
        prefix (str, optional): Leading indentation for each generated node. Default: "".

    Returns:
        list[:class:`parso.python.tree.String`]: The parso nodes which represent the given `data`.

    """
    return [
        tree.String(
            '"{requirement}"'.format(requirement=requirement.replace('"', '"')),
            (0, 0),
            prefix="\n{prefix}".format(prefix=prefix),
        )
        for requirement in data
    ]


def _merge_list_entries(old, new):
    """Apply `new` onto `old`.

    Args:
        old (list[:class:`parso.python.tree.String`]):
            The Rez requirements that will be modified.
        new (list[:class:`parso.python.tree.String`]):
            New (or existing) Rez requirements to add on top of `old`.

    Returns:
        list[:class:`parso.python.tree.String`]: The merge of `old` and `new`.

    """

    def _find_index(nodes, text):
        for index, node in enumerate(nodes):
            requirement = _escape(node.value)
            requirement = rez_requirement.Requirement(requirement)

            if requirement.name > text:
                return index

        return len(nodes)

    old = _remove_existing_entries(old, new)

    for entry in new:
        requirement = rez_requirement.Requirement(_escape(entry.value))
        index = _find_index(old, requirement.name)
        old.insert(index, entry)

    return old


def _node_to_requirement(node):
    """:class:`rez.vendor.version.requirement.Requirement`: Convert an AST node to a Rez."""
    requirement_text = _escape(node.value)

    return rez_requirement.Requirement(requirement_text)


def _remove_existing_entries(old, new):
    """Remove any entries of `old` that also exist in `new`.

    Args:
        old (list[:class:`parso.python.tree.String`]):
            The Rez requirements that may be removed.
        new (list[:class:`parso.python.tree.String`]):
            Any Rez requirements that should be removed from `old`.

    Returns:
        list[:class:`parso.python.tree.String`]:
            A modified version of `old` that doesn't contain anything from `new`.

    """
    old = copy.deepcopy(old)

    # Since `requires` doesn't really play nice with duplicate entries,
    # we will remove any existing requirements that match any entries in `new`.
    #
    for entry in reversed(new):
        new_requirement = rez_requirement.Requirement(_escape(entry.value))
        package_family = new_requirement.name

        for requirement in reversed(old):
            old_requirement = rez_requirement.Requirement(_escape(requirement.value))

            if old_requirement.name == package_family:
                index = old.index(requirement)

                del old[index]

    return old


def _resolve_data_conflicts(new, existing):
    """Change the upper / lower bounds of each requirement in `new`, if needed.

    The logic goes like this:

    - Compare each requirement by-name in `new` and `existing`
        - Apply whichever requirement's lower bound is highest.
            - Because we probably need to apply a new requirement minimum.
        - Apply whichever requirement's upper bound is highest.
            - We assume that the user has taken into account the higher upper bound.

    Args:
        new (iter[str]):
            Each Rez package requirement to compare / change.
            e.g. ["foo-1+<2"].
        existing (iter[:class:`rez.vendor.version.requirement.Requirement`]):
            Each Rez requirement to compare against.

    Returns:
        list[str]: The newly generated requirements for `new`.

    """
    new = (rez_requirement.Requirement(requirement) for requirement in new)
    new = collections.OrderedDict(
        [(requirement.name, requirement) for requirement in new]
    )
    existing = {requirement.name: requirement for requirement in existing}

    for name, requirement in new.items():
        if name not in existing:
            continue

        range_ = existing[name].range
        lower = max(
            [
                bound.lower
                for bound in itertools.chain(range_.bounds, requirement.range.bounds)
                if bound.lower_bounded()
            ]
        )
        upper = max(
            [
                bound.upper
                for bound in itertools.chain(range_.bounds, requirement.range.bounds)
                if bound.upper_bounded()
            ]
        )
        temporary_range = rez_version.VersionRange.as_span(
            lower_version=lower.version,
            upper_version=upper.version,
            lower_inclusive=lower.inclusive,
            upper_inclusive=upper.inclusive,
        )
        requirement.range_ = temporary_range

    return [str(requirement) for requirement in new.values()]
