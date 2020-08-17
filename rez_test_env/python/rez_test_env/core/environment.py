#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The main module which does all of the work of `rez_test_env`.

It parses the user's Rez test information, converts it into a Rez
package request, and appends those package(s) to the command which gets
sent to `rez-env`.

"""

import contextlib
import collections
import fnmatch
import sys

from rez import packages
from rez.cli import _main

from . import exceptions


@contextlib.contextmanager
def _keep_argv(override):
    """Temporarily replace :obj:`sys.argv` with `override` in a Python context.

    Args:
        override (list[str]): The new text to fake as user-provided text.

    Yields:
        A context which has the overwritten :attr:`sys.argv`.

    """
    original = list(sys.argv)

    try:
        sys.argv[:] = override

        yield
    finally:
        sys.argv[:] = original


def _expand_requirements(package, tests):
    package_tests = package.tests or set()
    requirements = set()

    real_test_names = _get_test_names(tests, package_tests)

    for name in real_test_names:
        details = package_tests[name]

        if isinstance(details, collections.Mapping):
            requirements.update([str(item) for item in details.get("requires") or []])

    return requirements


def _get_test_names(expressions, package_tests):
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
        raise exceptions.MissingTests('Tests "{invalids}" are missing.'.format(invalids=sorted(invalids)))

    return output


def _validate(package, tests):
    package_tests = package.tests or set()

    missing = {test for test in tests if test not in package_tests}

    if missing:
        raise exceptions.MissingTests('Package "{package}" has missing test names "{missing}".'.format(package=package, missing=", ".join(sorted(missing))))


def run(package_request, tests):
    package = packages.get_latest_package_from_string(package_request)

    if not package:
        raise exceptions.NoValidPackageFound('Request "{package_request}" doesn\'t match a Rez package.'.format(package_request=package_request))

    requirements = _expand_requirements(package, tests)

    with _keep_argv([package_request] + sorted(requirements)):
        _main.run("env")
