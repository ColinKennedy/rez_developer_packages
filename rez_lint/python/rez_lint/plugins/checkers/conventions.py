#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""A collection of issues that are less problematic than those found in :mod:`dangers`."""

from ...core import message_description, package_parser
from . import base_checker


class SemanticVersioning(base_checker.BaseChecker):
    """Check that the Rez package follows X.Y.Z versioning.

    Rez states explicitly in their code that semantic versioning is
    recommended. Also, from personal experience, using packages without
    semantic versioning makes working with said packages in the Rez API
    **very** painful.

    See Also:
        https://github.com/nerdvegas/rez/wiki/Basic-Concepts#versions

    """

    @staticmethod
    def get_long_code():
        """str: The string used to refer to this class or disable it."""
        return "semantic-versioning"

    @classmethod
    def run(cls, package, _):
        """Check the package for semantic versioning.

        Args:
            package (:class:`rez.packages_.DeveloperPackage`):
                The Rez package to check.

        Returns:
            list[:class:`.Description`]:
                If the package uses a scheme other than semantic
                versioning, flag it.

        """
        version = package.version

        if not _has_missing_numbers(version):
            return []

        summary = "Package is not X.Y.Z semantic versioning.".format(package=package)
        full = [
            summary,
            'Package {package.filepath}" has version "{package.version}".'.format(
                package=package
            ),
            "See https://semver.org for more details.",
        ]

        row = package_parser.get_definition_row(package.filepath, "version")
        text = package_parser.get_line_at_row(package.filepath, row)

        location = message_description.Location(
            path=package.filepath, row=row, column=0, text=text,
        )

        code = base_checker.Code(short_name="C", long_name=cls.get_long_code())

        return [
            message_description.Description([summary], location, code=code, full=full),
        ]


def _has_missing_numbers(version):
    """bool: Check if the given Rez version isn't using semantic versioning."""
    for attribute in ["major", "minor", "patch"]:
        try:
            getattr(version, attribute)
        except IndexError:
            return True

    return False
