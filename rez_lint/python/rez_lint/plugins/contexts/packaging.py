#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""A module for context plugins that are slow or difficult to query."""

import collections
import logging
import os
import re
import subprocess

from python_compatibility import filer
from rez import exceptions, resolved_context
from rez.config import config
from rez_utilities import inspection

from ...core import lint_constant
from . import base_context

_LOGGER = logging.getLogger(__name__)
_DEPENDENCY_PATHS_SCRIPT = os.environ["PYTHON_COMPATIBILITY_DEPENDENCY_PATHS_SCRIPT"]


class HasPythonPackage(base_context.BaseContext):
    """Find out if a Rez package defines a Python package and cache the result."""

    @staticmethod
    def run(package, context):
        """Add context information to `context`, using data inside of `package`.

        Args:
            package (:class:`rez.packages_.DeveloperPackage`):
                The Rez package to query information from.
            context (:class:`.Context`):
                An object that will be modified by this method with
                new data. You're free to do whatever you want to this
                parameter - add, modify, or delete any data you'd like.

        """
        try:
            has_package = inspection.has_python_package(package, allow_build=False)
        except exceptions.PackageFamilyNotFoundError:
            _LOGGER.warning(
                'Package "%s" triggered an error so it cannot be checked for Python modules',
                package,
            )
            has_package = False

        context[lint_constant.HAS_PYTHON_PACKAGE] = has_package


class SourceResolvedContext(base_context.BaseContext):
    """Make a resolved context around the user's source Rez package.

    Also, while the context exists, grab any Python dependencies and return those.

    """

    @staticmethod
    def run(package, context):
        """Get the resolved Rez context and add it to ``rez_lint``'s main context.

        Args:
            package (:class:`rez.packages_.DeveloperPackage`):
                The Rez package that will be resolved and queried.
            context (:class:`.Context`):
                The object that stores all of the cached results.

        """
        try:
            rez_context = _resolve(package)
        except exceptions.RezError:
            _LOGGER.exception('Package "%s" could not be resolved.', package)

            return

        python_package_roots = _get_package_specific_python_paths(package)
        dependency_paths = _search_for_python_dependencies(
            rez_context, python_package_roots
        )

        packages = _get_root_rez_packages(dependency_paths)
        packages = {package_ for package_ in packages if package_.name != package.name}

        context[lint_constant.RESOLVED_SOURCE_CONTEXT] = rez_context
        context[lint_constant.DEPENDENT_PACKAGES] = packages


def _search_for_python_dependencies(context, directories):
    """Find every Python file dependency for a set of directories.

    Args:
        context (:class:`rez.resolved_context.ResolvedContext`):
            The runtime environment that will be used to query the dependencies.
        directories (iter[str]):
            The absolute path to folders on-disk that will be used to
            search for Python files. The Python files get imported and
            directly searched for dependency files.

    Returns:
        set[str]: The found Python file dependencies.

    """
    directories = " ".join(['"{path}"'.format(path=path) for path in directories])
    process = context.execute_command(
        "{_DEPENDENCY_PATHS_SCRIPT} {directories}".format(
            _DEPENDENCY_PATHS_SCRIPT=_DEPENDENCY_PATHS_SCRIPT, directories=directories
        ),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    stdout, stderr = process.communicate()

    _LOGGER.debug("Found stdout")
    _LOGGER.debug(stdout)

    # If it's not a log message, then it must be some kind of error
    stderr_lines = [
        line
        for line in stderr.splitlines()
        if not line.startswith(("ERROR:", "INFO:", "WARNING:"))
    ]

    if stderr_lines:
        _LOGGER.error("Could not get Python path dependencies")
        _LOGGER.error(stderr)

        return []

    stdout_lines = filter(None, (line for line in stdout.splitlines()))

    return set(line for line in stdout_lines if os.path.isfile(line))


def _get_package_specific_environment(package):
    def _append(values, item):
        values.append(item)

    def _prepend(values, item):
        values.insert(0, item)

    def _set(values, item):
        values[:] = [item]

    options = [
        (re.compile(r"^\s*env\.(?P<key>\w+).append\s*\((?P<value>.+)\)"), _append),
        (re.compile(r"^\s*env\.(?P<key>\w+).prepend\s*\((?P<value>.+)\)"), _prepend),
        (re.compile(r"^\s*env\.(?P<key>\w+).set\s*\((?P<value>.+)\)"), _set),
        (re.compile(r"^\s*appendenv\s*\((?P<key>\w+),\s*(?P<value>.+)\)"), _append),
        (re.compile(r"^\s*prependenv\s*\((?P<key>\w+),\s*(?P<value>.+)\)"), _prepend),
        (re.compile(r"^\s*setenv\s*\((?P<key>\w+),\s*(?P<value>.+)\)"), _set),
    ]
    variables = collections.defaultdict(list)

    commands = package.commands

    if not commands:
        return dict()

    for line in commands.evaluated_code.splitlines():
        for option, caller in options:
            match = option.match(line)

            if match:
                variable = variables[match.group("key")]
                raw_text = match.group("value")
                code = eval(raw_text, {"os": os})
                caller(variable, code)

    return dict(variables)


def _get_package_specific_python_paths(package):
    """Open `package` and check the paths that it adds to the user's PYTHONPATH.

    Args:
        package (:class:`rez.packages_.Package`):
            The Rez package that modifies the user's PYTHONPATH
            environment variable with path information.

    Returns:
        list[str]: The found paths that `package`adds to the PYTHONPATH.

    """
    # TODO : Replace `_get_package_specific_environment` with my filer checker approach
    package_variables = _get_package_specific_environment(package)
    root = inspection.get_package_root(package)

    return [path.format(root=root) for path in package_variables.get("PYTHONPATH", [])]


def _get_root_rez_packages(paths):
    """Convert a list of file / folder paths into Rez package definitions.

    If a path in `paths` does not point to a Rez package then it is ignored.

    Args:
        paths (iter[str]):
            The paths to file(s) / folder(s) on-disk. These paths
            ideally should always be contained in other Rez packages.

    Returns:
        set[:class:`rez.developer_package.DeveloperPackage`]: The found Rez packages.

    """

    def _is_root_already_found(path, roots):
        """bool: If `path` is in a Rez package that was already found."""
        return any(True for root in roots if filer.in_directory(path, root))

    packages = dict()
    package_roots = set()

    for path in paths:
        if _is_root_already_found(path, package_roots):
            continue

        package = inspection.get_nearest_rez_package(path)

        if package:
            packages[package.name] = package
        else:
            _LOGGER.warning('Path "%s" has no Rez package.', path)

    return set(packages.values())


def _resolve(package):
    """Make a resolved context of the given Rez package + :mod:`python_compatibility`.

    Warning:
        This function may not behavior normally if `package` contains variants.

    Args:
        package (:class:`rez.packages_.Package`):
            The reference that will be converted into a context.

    Returns:
        :class:`rez.resolved_context.ResolvedContext`: The created context.

    """
    version = ""

    if inspection.is_built_package(package):
        version = package.version

    return resolved_context.ResolvedContext(
        [
            "{package.name}=={version}".format(package=package, version=version),
            "python_compatibility",
        ],
        package_paths=[inspection.get_packages_path_from_package(package)]
        + config.packages_path,  # pylint: disable=no-member
    )
