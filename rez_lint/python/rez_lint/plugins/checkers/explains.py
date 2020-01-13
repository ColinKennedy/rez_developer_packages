#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The full collection of plugins that ask the user to add more details to a package."""

import os

from python_compatibility.sphinx import conf_manager
from rez_utilities import inspection

from ...core import lint_constant, message_description
from . import base_checker


class _MissingFile(base_checker.BaseChecker):  # pylint: disable=abstract-method
    """Check for the existence of a file near a Rez package."""

    _file_name = ""
    _summary = ""

    @classmethod
    def run(cls, package, _):
        """Find a README.md file using a Rez package.

        Args:
            package (:class:`rez.packages_.DeveloperPackage`):
                The Rez package whose root directory will be used to
                search for a README file.

        Returns:
            list[:class:`.Description`]:
                If no issues are found, return an empty list. Otherwise,
                return one description of each found issue.

        """
        root = inspection.get_package_root(package)

        if cls._file_name in [os.path.splitext(name)[0] for name in os.listdir(root)]:
            return []

        code = base_checker.Code(short_name="E", long_name=cls.get_long_code())

        location = message_description.Location(path=root, row=0, column=0, text="",)

        return [
            message_description.Description([cls._summary], location, code=code),
        ]


class NoChangeLog(_MissingFile):
    """Check that some kind of explanation file (README.md / README.rst / etc) exists."""

    _file_name = "CHANGELOG"
    _summary = "Rez package has no CHANGELOG file"

    @staticmethod
    def get_long_code():
        """str: The string used to refer to this class or disable it."""
        return "no-change-log"


class NoDocumentation(base_checker.BaseChecker):
    """Find documentation for the user's Rez package and report if it's missing."""

    @staticmethod
    def get_long_code():
        """str: The string used to refer to this class or disable it."""
        return "no-documentation"

    @classmethod
    def run(cls, package, context):
        """Find a documentation for the Rez package.

        Args:
            package (:class:`rez.packages_.DeveloperPackage`):
                The Rez package that may or may not need documentation.
            context (:class:`.Context`):
                A data instance that knows whether `package` has a
                Python package. If there's no Python package, this
                checker is cancelled.

        Returns:
            list[:class:`.Description`]:
                If no issues are found, return an empty list. Otherwise,
                return one description of each found issue.

        """
        if not context[lint_constant.HAS_PYTHON_PACKAGE]:
            return []

        root = inspection.get_package_root(package)

        if conf_manager.get_conf_file(root):
            return []

        summary = "No documentation found"
        full = [
            summary,
            "Consider adding documentation to your Python package.",
            "Reference: https://www.sphinx-doc.org/en/master/usage/quickstart.html",
        ]
        code = base_checker.Code(short_name="E", long_name=cls.get_long_code())
        location = message_description.Location(path=root, row=0, column=0, text="")

        return [
            message_description.Description([summary], location, code=code, full=full),
        ]


class NoReadMe(_MissingFile):
    """Check that some kind of explanation file (README.md / README.rst / etc) exists."""

    _file_name = "README"
    _summary = "Rez package has no README file"

    @staticmethod
    def get_long_code():
        """str: The string used to refer to this class or disable it."""
        return "no-read-me"
