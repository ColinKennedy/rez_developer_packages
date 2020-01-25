#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""A collection of issues that bring harm to the current Rez package or others."""

import collections
import logging
import os

from python_compatibility import website
from rez_utilities import inspection, url_help

from ...core import lint_constant, message_description, package_parser
from . import base_checker

_LOGGER = logging.getLogger(__name__)


# TODO : Make the same class for build_requires and private_build_requires

class DuplicateDependencies(base_checker.BaseChecker):
    @staticmethod
    def _get_duplicate_requirements(requirements):
        counter = collections.Counter([requirement.name for requirement in requirements])

        return {package_name for package_name, count in counter.most_common() if count > 1}

    @classmethod
    def _get_duplicate_requirements_message(cls, package, duplicates):
        if len(duplicates) == 1:
            beginning = "A Rez package was"
        else:
            beginning = "Multiple Rez packages were"

        summary = beginning + " listed in ``requires`` more than once"

        full = [
            summary,
            'Requirements should only list each Rez package once. '
            'But "{duplicates}" requirements was listed multiple times.'.format(
                duplicates=sorted(duplicates))
        ]

        row = package_parser.get_definition_row(package.filepath, "requires")
        code = base_checker.Code(short_name="D", long_name=cls.get_long_code())
        text = package_parser.get_line_at_row(package.filepath, row)

        location = message_description.Location(
            path=package.filepath, row=row, column=0, text=text,
        )

        return [
            message_description.Description([summary], location, code=code, full=full),
        ]

    @staticmethod
    def get_long_code():
        """str: The string used to refer to this class or disable it."""
        return "duplicate-dependencies"

    @classmethod
    def run(cls, package, _):
        requirements = package.requires or []
        variants = package.variants or []

        if not requirements and not variants:
            return []

        issues = []
        duplicate_requirements = cls._get_duplicate_requirements(requirements)

        if duplicate_requirements:
            issues.extend(cls._get_duplicate_requirements_message(package, duplicate_requirements))

        return issues

        # TODO : Finish
        # duplicate_variants = cls._get_duplicate_variants(variants)
        #
        # if duplicate_variants:
        #     issues.append(cls._get_duplicate_variants_messgae(package, duplicate_variants))

        return issues


class ImproperRequirements(base_checker.BaseChecker):
    """A checker that makes sure the user doesn't put weird requirements in their Rez packages.

    Build requirements should be placed in the
    ``private_build_requires`` or ``build_requires`` attribute. Testing
    frameworks go in the ``tests`` attribute, as secondary requirements.
    They shouldn't be added to the required packages.

    Attributes:
        _blacklisted_build_packages (frozenset[str]):
            Build systems shouldn't be Rez requirements. This is the
            full list of known build-system-related packages.
        _blacklisted_unittest_packages (frozenset[str]):
            Unittest systems shouldn't be Rez requirements. This is the
            full list of known systems that are used to create tests.

    """

    _blacklisted_build_packages = frozenset(("cmake",))
    _blacklisted_unittest_packages = frozenset(
        (
            "coverage",  # Reference: https://pypi.org/project/coverage
            "mock",  # Reference: https://pypi.org/project/mock
            "nose",  # Reference: https://pypi.org/project/nose
            "nose2",  # Reference: https://pypi.org/project/nose2
            "pyexpect",  # Reference: https://pypi.org/project/pyexpect
            "pytest",  # Reference: https://pypi.org/project/pytest
            "unittest-additions",  # Reference: https://pypi.org/project/unittest-additions
            "unittest2",  # Reference: https://pypi.org/project/unittest2
        )
    )

    @classmethod
    def _get_build_messages(cls, package, dependencies):
        summary = "Improper build package requirements were found"

        full = [
            summary,
            'Requirements "{impropers}" should not be in requires. '
            "Instead, they should be either defined "
            "in the ``private_build_requires`` or ``build_requires`` attribute.".format(
                impropers=sorted(request.name for request in dependencies)
            ),
        ]

        row = package_parser.get_definition_row(package.filepath, "requires")
        code = base_checker.Code(short_name="D", long_name=cls.get_long_code())
        text = package_parser.get_line_at_row(package.filepath, row)

        location = message_description.Location(
            path=package.filepath, row=row, column=0, text=text,
        )

        return [
            message_description.Description([summary], location, code=code, full=full),
        ]

    @classmethod
    def _get_unittest_messages(cls, package, dependencies):
        summary = "Improper unittest package requirements were found"

        full = [
            summary,
            'Requirements "{impropers}" should not be in requires. '
            "Instead, they should be defined as part of the package's ``tests`` attribute."
            "".format(impropers=sorted(request.name for request in dependencies)),
        ]

        row = package_parser.get_definition_row(package.filepath, "requires")
        code = base_checker.Code(short_name="D", long_name=cls.get_long_code())
        text = package_parser.get_line_at_row(package.filepath, row)

        location = message_description.Location(
            path=package.filepath, row=row, column=0, text=text,
        )

        return [
            message_description.Description([summary], location, code=code, full=full),
        ]

    @staticmethod
    def get_long_code():
        """str: The string used to refer to this class or disable it."""
        return "improper-requirements"

    @classmethod
    def run(cls, package, _):
        """Check if `package` depends on a Rez package that it shouldn't.

        Args:
            package (:class:`rez.packages_.DeveloperPackage`):
                The Rez package whose requirements may include unittest
                or build, related requirements.

        Returns:
            list[:class:`.Description`]:
                If `package` depends on something weird, like "mock" or "cmake".

        """
        requirements = package.requires or []
        improper_unittest_dependencies = []
        improper_build_dependencies = []

        for requirement in requirements:
            if requirement.name in cls._blacklisted_build_packages:
                improper_build_dependencies.append(requirement)
            if requirement.name in cls._blacklisted_unittest_packages:
                improper_unittest_dependencies.append(requirement)

        results = []

        if improper_build_dependencies:
            results.extend(
                cls._get_build_messages(package, improper_build_dependencies)
            )

        if improper_unittest_dependencies:
            results.extend(
                cls._get_unittest_messages(package, improper_unittest_dependencies)
            )

        return results


class MissingRequirements(base_checker.BaseChecker):
    """Check that a Rez package's requirements are up to date."""

    @staticmethod
    def get_long_code():
        """str: The string used to refer to this class or disable it."""
        return "missing-requirements"

    @classmethod
    def run(cls, package, context):
        """Check that a Rez package's requirements are up to date.

        Args:
            package (:class:`rez.packages_.DeveloperPackage`):
                The Rez package whose requirements may be missing a
                package or an existing package has the wrong version
                information.
            context (:class:`.Context`):
                A data instance that knows whether `package` has a
                Python package and also keeps track of the Rez package's
                list of dependencies. This list of dependencies are
                modules imported by the Rez package (these dependencies)
                should hopefully always match the Rez package's list of
                requirements.

        Returns:
            list[:class:`.Description`]: The found requirement problems, if any.

        """
        if not context[lint_constant.HAS_PYTHON_PACKAGE]:
            return []

        listed_requirements = {
            package_.name: package_ for package_ in package.requires or []
        }

        missing = []

        for package_ in context[lint_constant.DEPENDENT_PACKAGES]:
            if package_.name not in listed_requirements:
                missing.append(package_)

        if not missing:
            return []

        summary = "Missing Package requirements"
        full = [
            summary,
            "The following requirements are missing and must be added.",
            'Full list "{missing}".'.format(
                missing=[package_.name for package_ in missing]
            ),
        ]

        row = package_parser.get_definition_row(package.filepath, "requires")
        code = base_checker.Code(short_name="D", long_name=cls.get_long_code())
        text = package_parser.get_line_at_row(package.filepath, row)

        location = message_description.Location(
            path=package.filepath, row=row, column=0, text=text,
        )

        return [
            message_description.Description([summary], location, code=code, full=full),
        ]


class RequirementLowerBoundsMissing(base_checker.BaseChecker):
    """Check that the user is practicing good bounds standards.

    e.g.

    .. code-block :: python

        requires = ["some_dependency"]

    This dependency forces Rez to search every released version of a
    dependency and then cross-reference that dependency with every other
    Rez package in the request + its requirements.

    .. code-block :: python

        requires = ["some_dependency-2+"]

    This does the same thing, but excludes 1.X releases. Other Rez
    package versions in the request may require 1+<2, which means
    that including a lower bound has the decreasing Rez resolve time
    quadratically. So it's always a good idea to have a lower bound.

    """

    @staticmethod
    def get_long_code():
        """str: The string used to refer to this class or disable it."""
        return "lower-bounds-missing"

    @classmethod
    def run(cls, package, _):
        """Check the package for any requirement that has no lower bounds.

        Args:
            package (:class:`rez.packages_.DeveloperPackage`):
                The Rez package that may contain requirements that are
                too permissive.

        Returns:
            list[:class:`.Description`]:
                If any requirements are found without lower bounds,
                return them as text.

        """
        requirements = package.requires or []
        missing_bounds = [
            requirement
            for requirement in requirements
            if not requirement.range_.lower_bounded()
        ]

        if not missing_bounds:
            return []

        summary = "Package requires are missing a minimum version"
        full = [
            summary,
            'Requirements "{missing_bounds}" have no minimum version.'.format(
                missing_bounds=[str(requires) for requires in missing_bounds],
            ),
        ]

        row = package_parser.get_definition_row(package.filepath, "requires")
        code = base_checker.Code(short_name="D", long_name=cls.get_long_code())
        text = package_parser.get_line_at_row(package.filepath, row)

        location = message_description.Location(
            path=package.filepath, row=row, column=0, text=text,
        )

        return [
            message_description.Description([summary], location, code=code, full=full),
        ]


class RequirementsNotSorted(base_checker.BaseChecker):
    """Check that requirements are kept alphabetically sorted."""

    @staticmethod
    def get_long_code():
        """str: The string used to refer to this class or disable it."""
        return "requirements-not-sorted"

    @classmethod
    def run(cls, package, _):
        """Check the package for unsorted requirements.

        Args:
            package (:class:`rez.packages_.DeveloperPackage`):
                The Rez package that may contain requirements that are
                out of order.

        Returns:
            list[:class:`.Description`]:
                If any requirements aren't sorted alphabetically, return
                them as text.

        """
        requirements = package.requires or []

        sorted_requirements = sorted(requirements, key=str)

        if requirements == sorted_requirements:
            return []

        summary = "Package requirements are not sorted"
        full = [
            summary,
            'Expected order: "{sorted_requirements}"'.format(
                sorted_requirements=[str(requires) for requires in sorted_requirements],
            ),
        ]

        row = package_parser.get_definition_row(package.filepath, "requires")
        code = base_checker.Code(short_name="D", long_name=cls.get_long_code())
        text = package_parser.get_line_at_row(package.filepath, row)

        location = message_description.Location(
            path=package.filepath, row=row, column=0, text=text,
        )

        return [
            message_description.Description([summary], location, code=code, full=full),
        ]


class NotPythonDefinition(base_checker.BaseChecker):
    """Check if the Rez package is package.yaml, package.txt, or some other package.py standard."""

    @staticmethod
    def get_long_code():
        """str: The string used to refer to this class or disable it."""
        return "not-python-definition"

    @classmethod
    def run(cls, package, _):
        """Check if `package` is defined using a "package.py" file or something else.

        Args:
            package (:class:`rez.packages_.DeveloperPackage`):
                The Rez package to check. This package most likely
                will be a package.yaml or package.py file.

        Returns:
            list[:class:`.Description`]:
                If `package` is defined using anything other than a package.py file.

        """
        path = package.filepath

        if os.path.splitext(path)[-1].endswith(".py"):
            return []

        summary = "Using a non-Python Rez package definition file"
        full = [
            summary,
            "Rez may support non-Python files such as package.yaml and package.txt "
            "they are inferior to package.py.",
            "Many Rez features are only available in Python. "
            "Such as @early() and @late() decorators.",
            "Please switch to package.py at once.",
        ]
        code = base_checker.Code(short_name="D", long_name=cls.get_long_code())

        location = message_description.Location(
            path=package.filepath, row=0, column=0, text="",
        )

        return [
            message_description.Description([summary], location, code=code, full=full),
        ]


class NoRezTest(base_checker.BaseChecker):
    """Check for tests in the current Rez package."""

    @staticmethod
    def get_long_code():
        """str: The string used to refer to this class or disable it."""
        return "no-rez-test"

    @classmethod
    def run(cls, package, _):
        """Check if a Rez package has any tests.

        Args:
            package (:class:`rez.packages_.DeveloperPackage`):
                The Rez package that may contain requirements that are
                out of order.

        Returns:
            list[:class:`.Description`]:
                If any requirements aren't sorted alphabetically, return
                them as text.

        """
        tests = package.tests or []

        if tests:
            return []

        summary = "Package has no rez-test attribute defined"
        full = [
            summary,
            "Reference: https://github.com/nerdvegas/rez/wiki/Package-Definition-Guide#tests",
        ]
        code = base_checker.Code(short_name="D", long_name=cls.get_long_code())

        location = message_description.Location(
            path=package.filepath, row=0, column=0, text="",
        )

        return [
            message_description.Description([summary], location, code=code, full=full),
        ]


class TooManyDependencies(base_checker.BaseChecker):
    """Check if a Rez package is in danger of becoming bloated and hard to work with."""

    _maximum_dependencies = 10

    @staticmethod
    def get_long_code():
        """str: The string used to refer to this class or disable it."""
        return "too-many-dependencies"

    @classmethod
    def run(cls, package, _):
        """Run the checker. Find out if `package` is bloated.

        Args:
            package (:class:`rez.packages_.Package`):
                A Rez package that may have too many dependencies listed
                in its ``requires`` attribute.

        Returns:
            list[:class:`.Description`]: If `package` is too large.

        """
        requirements = package.requires or []
        current = len(requirements)

        if current < cls._maximum_dependencies:
            return []

        summary = (
            "Package has too many dependencies ({current}/{cls._maximum_dependencies})"
            "".format(current=current, cls=cls)
        )

        full = [
            summary,
            "This package has many dependencies, which limits its portability, "
            "usefulness, and will increase resolve time.",
            "Consider moving dependencies to "
            "``tests``, ``private_build_requires``, or ``build_requires``.",
            "Or move helper functions / classes to a separate utility Rez package to reduce load.",
        ]

        location = message_description.Location(
            path=package.filepath, row=0, column=0, text="",
        )
        code = base_checker.Code(short_name="D", long_name=cls.get_long_code())

        return [
            message_description.Description([summary], location, code=code, full=full),
        ]


class UrlNotReachable(base_checker.BaseChecker):
    """Check every rez-test URL destination to make sure it exists.

    If for any reason the Internet is down, just skip the test.

    """

    @staticmethod
    def _filter_existing_paths(urls, root):
        """Return all Rez help entries that don't point to file(s)/folder(s) on-disk.

        Args:
            urls (iter[tuple[int, str, str]]):
                The entry number in a Rez package's ``help`` attribute,
                the human-readable label that was added to identify it,
                and the command, URL, or file path that was chosen.
            root (str):
                An absolute path to a directory on disk. If a relative
                path is found as a part of `urls`, this path is used to
                resolve that relative path into an absolute one.

        Returns:
            list[tuple[int, str, str]]:
                The given `urls` that are not a valid file or folder on-disk.

        """
        invalids = []

        for index, label, url in urls:
            if os.path.isabs(url):
                if not os.path.exists(url):
                    invalids.append((index, label, url))

                continue  # pragma: no cover

            possible_existing_path = os.path.normpath(os.path.join(root, url))

            if not os.path.exists(possible_existing_path):
                invalids.append((index, label, url))

        return invalids

    @staticmethod
    def get_long_code():
        """str: The string used to refer to this class or disable it."""
        return "url-unreachable"

    @classmethod
    def run(cls, package, _):
        """Find every URL in a Rez package that points to a bad web address.

        If the Internet is down, this method returns empty and is skipped.

        Args:
            package (:class:`rez.packages_.Package`):
                A Rez package that may have a ``help`` attribute/function defined.
                This attribute will be checked for issues.
            _: An un-used argument.

        """
        if not package.help:
            return []

        if not website.is_internet_on():
            _LOGGER.warning(
                "User has no internet. Checking for help URLs will be skipped."
            )

            return []

        urls = url_help.get_invalid_help_urls(package)

        if not urls:
            return []

        urls = cls._filter_existing_paths(urls, inspection.get_package_root(package))

        if not urls:
            return []

        summary = "Package help has an un-reachable URL"
        urls = sorted([(label, url) if label else url for _, label, url in urls])
        full = [
            summary,
            'Found URLs are un-reachable "{urls}".'.format(urls=urls),
        ]

        row = package_parser.get_definition_row(package.filepath, "help")
        location = message_description.Location(
            path=package.filepath, row=row, column=0, text="",
        )
        code = base_checker.Code(short_name="D", long_name=cls.get_long_code())

        return [
            message_description.Description([summary], location, code=code, full=full),
        ]
