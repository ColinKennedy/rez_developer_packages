#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""A module that prompts the user to explain their reasons for adding Rez package dependencies."""

import logging

from parso.python import tree

from ...core import (
    lint_constant,
    message_description,
    package_parser,
    parso_comment_helper,
)
from . import base_checker

_LOGGER = logging.getLogger(__name__)


class NeedsComment(base_checker.BaseChecker):
    """A checker that looks at a Rez package's ``requires`` to see if it needs explaining.

    If a requirement in the Rez package can be found as a dependency
    automatically, such as a Python import, then it doesn't need a
    comment.

    But if the package cannot be automatically found, it needs some kind
    of message to explain **why** it is there.

    """

    @staticmethod
    def get_long_code():
        """str: The string used to refer to this class or disable it."""
        return "needs-comment"

    @staticmethod
    def _get_comment_pairs(graph):
        """Get every Rez requirement string and its comment.

        Args:
            graph (list[:class:`parso.Graph`]):
                The parsed code that represents a Python module. This
                will usually be the "package.py" of a Rez package.

        Raises:
            EnvironmentError: If no valid "requires" attribute could be found in `graph`.

        Returns:
            dict[str, str]:
                The string or variable name and its commented value.
                e.g. {"rez": "The best thing to happen since sliced bread!"}.

        """
        node = parso_comment_helper.find_named_node(graph, "requires")

        if not isinstance(node, tree.Name):
            # This isn't supported yet but theoretically could be done
            raise EnvironmentError('Node "{node}" is not supported.'.format(node=node))

        full_definition = parso_comment_helper.get_full_name_definition(node)
        just_the_requirements = parso_comment_helper.trim_list_excess(full_definition)

        return parso_comment_helper.get_comment_pairs(just_the_requirements)

    @classmethod
    def run(cls, package, context):
        """Find any Rez package requirements that need explaining.

        Args:
            package (:class:`rez.packages_.DeveloperPackage`):
                The Rez package whose root directory will be used to
                search for a README file.
            context (:class:`.Context`):
                A data instance that has already parsed `package`
                in advance. If also contains a list of all of the
                Rez packages that `package` depends on. This list of
                dependencies are found from Python imports and isn't
                based on the user-provided requirements that you'd
                normally find in a Python package.py file.

        Returns:
            list[:class:`.Description`]:
                If no issues are found, return an empty list. Otherwise,
                return one description of each found issue.

        """
        graph = context.get(lint_constant.PARSO_GRAPH)

        if not graph:
            _LOGGER.info("NeedsComment class will not run because no graph was found.")

            return []

        try:
            pairs = cls._get_comment_pairs(graph)
        except EnvironmentError:
            _LOGGER.info(
                'The `requires` in "%s" is not an attribute so requirements cannot be checked.',
                package,
            )

            return []

        # TODO : use global variable
        dependencies = set(package.name for package in context["dependent_packages"])

        try:
            missing = _get_missing_comment_pairs(
                package.requires or [], pairs, dependencies
            )
        except EnvironmentError:
            return []

        if not missing:
            return []

        summary = "Requirement(s) are missing explanation"
        full = [
            summary,
            'Each requirement "{missing}" needs a comment to explain '
            "why it is a Rez package dependency.".format(missing=sorted(missing)),
        ]

        row = package_parser.get_definition_row(package.filepath, "requires")
        code = base_checker.Code(short_name="E", long_name=cls.get_long_code())
        text = package_parser.get_line_at_row(package.filepath, row)

        location = message_description.Location(
            path=package.filepath, row=row, column=0, text=text,
        )

        return [
            message_description.Description([summary], location, code=code, full=full),
        ]


def _get_missing_comment_pairs(requirements, pairs, dependencies):
    """Find every Rez requirement that is missing a comment string.

    Args:
        requirements (:class:`rez.packages_.Package`):
            The Rez packages that need to be checked for comments.
        pairs (dict[str, str]):
            The name of every Rez package and its existing comment, if
            any. is parameter is populated by the user's pre-existing
            package.py file.
        dependencies (set[str]):
            The detected Rez package names that the user's Rez package
            requires. This list is different from `requirements` because
            it is taken directly from the Rez package's Python imports,
            not from the package's ``requires`` attribute.

    Returns:
        set[str]: The names of every Rez package requirement that needs a comment.

    """
    requirements_to_check = [
        requirement.name
        for requirement in requirements
        if requirement.name not in dependencies
    ]

    if not requirements_to_check:
        return set()

    missing = set()

    for requirement in requirements_to_check:
        comment = pairs[requirement]

        if not comment:
            missing.add(requirement)

    return missing
