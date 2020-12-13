#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The main module which does all of the work of `rez_test_env`.

It parses the user's Rez test information, converts it into a Rez
package request, and appends those package(s) to the command which gets
sent to `rez-env`.

"""

import collections
import contextlib
import fnmatch
import logging
import os
import sys

from rez import exceptions as rez_exceptions
from rez.cli import _main
from rez.vendor.schema import schema

from . import exceptions

try:
    from rez import packages_ as packages
except ImportError:
    from rez import packages


_LOGGER = logging.getLogger(__name__)


@contextlib.contextmanager
def _patch_main(override):
    """Temporarily replace :obj:`sys.argv` with `override` in a Python context.

    Args:
        override (list[str]): The new text to fake as user-provided text.

    Yields:
        A context which has the overwritten :attr:`sys.argv`.

    """
    original = list(sys.argv)
    override = ["discarded_command"] + override

    try:
        sys.argv[:] = override

        yield
    finally:
        sys.argv[:] = original


def _expand_requirements(package, tests):
    """Convert a list of Rez test names into Rez package requests.

    Args:
        package (:class:`rez.packages.Package`):
            The Rez package to read test commands from. This package is
            **not** included in the output.
        tests (iter[str]):
            The user's raw CLI test input. These could be real test
            names, like "my_foo_unittest", or a glob expression, like
            "my_*_unittest".

    Returns:
        set[str]:
            The requirements needed to resolve `package` + the given
            `tests`.

    """
    package_tests = package.tests or set()
    requirements = set()

    real_test_names = _get_test_names(tests, package_tests)

    for name in real_test_names:
        details = package_tests[name]

        # Not all rez-test commands define extra requirements. Only add
        # the ones which do.
        #
        if isinstance(details, collections.Mapping):
            requirements.update([str(item) for item in details.get("requires") or []])

    _LOGGER.debug(
        'Expanded package/tests "%s/%s" into packages "%s".',
        package.name,
        tests,
        requirements,
    )

    return requirements


def _get_test_names(expressions, package_tests):
    """Find real rez-test command names from a list of `expressions`.

    Args:
        expressions (iter[str]):
            The user's raw CLI test input. These could be real test
            names, like "my_foo_unittest", or a glob expression, like
            "my_*_unittest".
        package_tests (list[str or dict[str]]):
            The test details of some Rez package. This is used to find
            the "real" test names.

    Raises:
        :class:`.MissingTests`:
            If any test in `expressions` couldn't be matched to at least
            one Rez test in `package_tests`.

    Returns:
        set[str]: The expanded rez-test command names.

    """
    output = set()
    invalids = set()

    for expression in expressions:
        found = False

        for name in package_tests:
            if fnmatch.fnmatch(name, expression):
                output.add(name)
                found = True

        if not found:
            invalids.add(expression)

    if invalids:
        raise exceptions.MissingTests(
            'Tests "{invalids}" are missing. Options were "{package_tests}".'.format(
                invalids=", ".join(sorted(invalids)),
                package_tests=sorted(package_tests.keys()),
            )
        )

    return output


def get_nearest_rez_package(directory):
    """Assuming that `directory` is on or inside a Rez package, find the nearest Rez package.

    This is copied from
    :func:`rez_utilities.finder.get_nearest_rez_package` to avoid the
    extra dependency.

    Args:
        directory (str):
            The absolute path to a folder on disk. This folder should be
            a sub-folder inside of a Rez package to the root of the Rez package.

    Returns:
        :class:`rez.developer_package.DeveloperPackage` or NoneType: The found package.

    """
    previous = None
    original = directory

    if not os.path.isdir(directory):
        directory = os.path.dirname(directory)

    while directory and previous != directory:
        previous = directory

        try:
            return packages.get_developer_package(directory)
        except (
            # This happens if the package in `directory` is missing required data
            rez_exceptions.PackageMetadataError,
            # This happens if the package in `directory` is written incorrectly
            schema.SchemaError,
        ):
            _LOGGER.debug('Directory "%s" found an invalid Rez package.', directory)

        directory = os.path.dirname(directory)

    _LOGGER.debug(
        'Directory "%s" is either inaccessible or is not part of a Rez package.',
        original,
    )

    return None


def run_from_request(package_request, tests):
    """Convert a Rez package + tests.

    See Also:
        https://github.com/nerdvegas/rez/wiki/Basic-Concepts#package-requests

    Args:
        package_request (str):
            The user's raw CLI input. It can be any Rez package request.
        tests (iter[str]):
            The user's raw CLI test input. These could be real test
            names, like "my_foo_unittest", or a glob expression, like
            "my_*_unittest".

    Raises:
        :class:`.NoValidPackageFound`:
            If `package_request` doesn't match a valid Rez package'

    """
    package = packages.get_latest_package_from_string(package_request)

    if not package:
        raise exceptions.NoValidPackageFound(
            'Request "{package_request}" doesn\'t match a Rez package.'.format(
                package_request=package_request
            )
        )

    _LOGGER.debug('Found package "%s".', package)

    requirements = _expand_requirements(package, tests)

    with _patch_main([package_request] + sorted(requirements)):
        _main.run("env")


def run_from_package(package, tests):
    """Create an environment from a Rez package + tests.

    Args:
        package (:class:`rez.packages.Package`):
            Some Rez package to include in the resolve.
        tests (iter[str]):
            The user's raw CLI test input. These could be real test
            names, like "my_foo_unittest", or a glob expression, like
            "my_*_unittest".

    """
    requirements = list(_expand_requirements(package, tests))
    package_request = ["{package.name}=={package.version}".format(package=package)]
    full_request = package_request + sorted(requirements)

    _LOGGER.debug('Making environment for "%s" request.', full_request)

    with _patch_main(full_request):
        _main.run("env")
