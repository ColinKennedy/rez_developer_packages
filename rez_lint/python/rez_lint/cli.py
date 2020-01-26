#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The main module that prints lint messages to the user."""

import importlib
import itertools
import logging
import operator
import os

from python_compatibility import wrapping
from rez import exceptions as rez_exceptions
from rez import packages_

from .core import exceptions, registry
from .plugins import check_context
from .plugins.checkers import (
    base_checker,
    conventions,
    dangers,
    explains,
    explains_comment,
)
from .plugins.contexts import base_context, packaging, parsing

_LOGGER = logging.getLogger(__name__)


def _search_current_folder(directory):
    """Find the user's Rez package or die trying.

    Args:
        directory (str):
            The absolute path to a folder which should have a package.py
            / package.yaml / package.txt underneath.

    Raises:
        :class:`.NoPackageFound`: If No Rez package could be found.

    Returns:
        :class:`rez.packages_.Package`: The found Rez package.

    """
    try:
        package = packages_.get_developer_package(directory)
    except rez_exceptions.PackageMetadataError:
        raise exceptions.NoPackageFound(
            'Directory "{directory}" does not define a Rez package.'.format(
                directory=directory
            )
        )

    if package:
        return package

    raise exceptions.NoPackageFound(
        'Directory "{directory}" does not define a Rez package.'.format(
            directory=directory
        )
    )


def _find_rez_packages(directory, recursive=False):
    """Get every Rez package starting from the current directory.

    Args:
        directory (str):
            The absolute path to a folder which should have a package.py
            / package.yaml / package.txt underneath.
        recursive (bool, optional):
            If False, only get the Rez package in the current folder. If
            True, get all Rez packages found on-or-below `directory`.
            Default is False.

    Raises:
        :class:`.NoPackageFound`: If No Rez package could be found.

    Returns:
        set[:class:`rez.packages_.Package`]: The found Rez package.

    """

    def _get_safe_package(path):
        try:
            return {packages_.get_developer_package(path)}
        except rez_exceptions.PackageMetadataError:
            return {}

    if not recursive:
        return {_search_current_folder(directory)}

    packages = _get_safe_package(directory)

    for root, folders, _ in os.walk(directory):
        for folder in folders:
            path = os.path.join(root, folder)
            packages.update(_get_safe_package(path))

    if not packages:
        raise exceptions.NoPackageFound(
            'Directory "{directory}" and its sub-folders '
            "do not define any Rez packages.".format(directory=directory)
        )

    return packages


@wrapping.run_once
def _register_external_plugins():
    """Add user plugins to the current ``rez_lint`` environment.

    If any user added their own context or checker plugins, this
    function will add them here.

    """
    environment = os.getenv("REZ_LINT_PLUGIN_PATHS")

    if not environment:
        _LOGGER.debug('No environment paths were "%s" found.')

        return

    _LOGGER.debug('Environment paths "%s" found.', environment)

    paths = []

    for namespace in environment.split(os.pathsep):
        if namespace not in paths:
            paths.append(namespace)

    for namespace in paths:
        _LOGGER.info('Importing module "%s".', namespace)
        importlib.import_module(namespace)

    registry.register_plugins(
        itertools.chain(
            base_checker.BaseChecker.__subclasses__(),
            base_context.BaseContext.__subclasses__(),
        )
    )


@wrapping.run_once
def _register_internal_plugins():
    """Add the plugins that ``rez_lint`` offers by default to the user.

    This function must run before :func:`_register_external_plugins` so
    that it has a chance to override the plugins created here.

    """
    registry.register_checker(conventions.SemanticVersioning)
    registry.register_checker(dangers.DuplicateBuildRequires)
    registry.register_checker(dangers.DuplicatePrivateBuildRequires)
    registry.register_checker(dangers.DuplicateRequires)
    registry.register_checker(dangers.ImproperRequirements)
    registry.register_checker(dangers.ImproperVariants)
    registry.register_checker(dangers.MissingRequirements)
    registry.register_checker(dangers.NoRezTest)
    registry.register_checker(dangers.NotPythonDefinition)
    registry.register_checker(dangers.RequirementLowerBoundsMissing)
    registry.register_checker(dangers.RequirementsNotSorted)
    registry.register_checker(dangers.TooManyDependencies)
    registry.register_checker(dangers.UrlNotReachable)
    registry.register_checker(explains.NoChangeLog)
    registry.register_checker(explains.NoDocumentation)
    registry.register_checker(explains.NoHelp)
    registry.register_checker(explains.NoReadMe)
    registry.register_checker(explains_comment.NeedsComment)
    registry.register_context(packaging.HasPythonPackage)
    registry.register_context(packaging.SourceResolvedContext)
    registry.register_context(parsing.ParsePackageDefinition)


def lint(
    directory, disable=frozenset(), vimgrep=False, recursive=False, verbose=False,
):
    """Print out issues with the Rez package(s) starting at a directory on-disk.

    Args:
        directory (str):
            The absolute path to a folder on-disk where at least one Rez
            package can be found.
        disable (set[str], optional):
            The issue codes that should be skipped by during this run.
            The default behavior skips nothing.
        vimgrep (bool, optional):
            If True, print out the lint information as path, row, and
            column information. If False, print the lint information in
            a more "human-readable" format. Default is False.
        recursive (bool, optional):
            If True, find every Rez package starting from `directory`.
            If False, only get the Rez package in the current directory.
            Default is False.
        verbose (bool, optional):
            If True, print the lint messages without summarizing any of its data.
            If False, only print 1-to-2 line summaries of each found issue.
            Default is False.

    Returns:
        list[:class:`.Description`]: Get the found issues.

    """
    _register_internal_plugins()
    _register_external_plugins()

    packages = _find_rez_packages(directory, recursive=recursive)
    output = set()
    processed_packages = []

    for package in packages:
        context = check_context.Context(
            package, list(processed_packages), vimgrep=vimgrep, verbose=verbose,
        )
        context["processed_checker"] = []
        context["processed_contexts"] = []

        for manager in sorted(
            registry.get_contexts(),
            key=operator.methodcaller("get_order"),
            reverse=True,
        ):
            manager.run(package, context)
            context["processed_contexts"].append(manager)

        for checker in sorted(
            registry.get_checkers(),
            key=operator.methodcaller("get_order"),
            reverse=True,
        ):
            if checker.get_long_code() in disable:
                context["processed_contexts"].append(
                    {"checker": checker, "status": "skipped"}
                )

                continue

            results = checker.run(package, context)
            context["processed_contexts"].append(
                {"checker": checker, "status": "ran", "results": results}
            )
            output.update(results)

        processed_packages.append(package)

    return sorted(output)
