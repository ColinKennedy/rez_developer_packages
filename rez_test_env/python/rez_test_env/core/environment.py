#!/usr/bin/env python
# -*- coding: utf-8 -*-

import contextlib
import sys

from rez.cli import _main

from . import exceptions


@contextlib.contextmanager
def _keep_argv(override):
    original = list(sys.argv)

    try:
        sys.argv[:] = override

        yield
    finally:
        sys.argv[:] = original


def _expand_requirements(package, tests):
    package_tests = package.tests or set()
    requirements = set()

    for name in tests:
        details = package_tests[name]

        requirements.update(details["requirements"])

    return requirements


def _validate(package, tests):
    package_tests = package.tests or set()

    missing = {test for test in tests if test not in package_tests}

    if missing:
        raise exceptions.MissingTests('Package "{package}" has missing test names "{missing}".'.format(package=package, missing=", ".join(sorted(missing))))


def run(package, tests):
    requirements = _expand_requirements(package, tests)

    with _keep_argv(package + sorted(requirements)):
        _main.run("env")
