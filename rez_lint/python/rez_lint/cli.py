#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The main module that prints lint messages to the user."""

import operator
import os

from rez import exceptions as rez_exceptions
from rez import packages_

from .core import exceptions, registry
from .plugins import check_context


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
    if not recursive:
        return {_search_current_folder(directory)}

    packages = set()

    for root, folders, _ in os.walk(directory):
        for folder in folders:
            path = os.path.join(root, folder)
            package = packages_.get_developer_package(path)

            if package:
                packages.add(package)

    if not packages:
        raise exceptions.NoPackageFound(
            'Directory "{directory}" and its sub-folders '
            "do not define any Rez packages.".format(directory=directory)
        )

    return packages


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
        list[:class:`Description`]: Get the found issues.

    """
    packages = _find_rez_packages(directory, recursive=recursive)
    output = set()
    processed_packages = []

    for package in packages:
        context = check_context.Context(
            package, list(processed_packages), vimgrep=vimgrep, verbose=verbose,
        )

        for manager in sorted(
            registry.get_contexts(),
            key=operator.methodcaller("get_order"),
            reverse=True,
        ):
            manager.run(package, context)

        for checker in sorted(
            registry.get_checkers(),
            key=operator.methodcaller("get_order"),
            reverse=True,
        ):
            if checker.get_long_code() in disable:
                continue

            output.update(checker.run(package, context))

        processed_packages.append(package)

    return sorted(output)
