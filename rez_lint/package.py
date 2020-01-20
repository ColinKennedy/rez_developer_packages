#!/usr/bin/env python
# -*- coding: utf-8 -*-

name = "rez_lint"

version = "1.0.0"

description = 'A "pylint" for Rez packages'

private_build_requires = ["rez_build_helper-1+<2"]

requires = [
    "backports.functools_lru_cache-1.6+<2",
    "parso-0+<1",
    "python-2+<3",
    "python_compatibility-1+<2",
    "rez-2.47+<3",
    "rez_utilities-1+<2",
    "six-1.13+<2",
]

build_command = "python -m rez_build_helper --items bin python"

tests = {
    "black_diff": {
        "command": "rez-env black -- black --diff --check package.py python tests"
    },
    "black": {"command": "rez-env black -- black package.py python tests"},
    "coverage": {
        "command": "coverage run --parallel-mode --include=python/* -m unittest discover && coverage combine --append && coverage html",
        "requires": ["coverage-4+<5", "mock-3+",],
    },
    "isort": {
        "command": "isort --recursive package.py python tests",
        "requires": ["isort"],
    },
    "isort_check": {
        "command": "isort --check-only --diff --recursive package.py python tests",
        "requires": ["isort"],
    },
    "pydocstyle": {
        # Need to disable D202 for now, until a new pydocstyle version is released
        # Reference: https://github.com/psf/black/issues/1159
        #
        "command": "rez-env pydocstyle -- pydocstyle --ignore=D213,D202,D203,D406,D407 python tests",
        "requires": ["pydocstyle"],
    },
    "pylint": {
        "command": "pylint --disable=bad-continuation python/rez_lint tests",
        "requires": ["pylint-1.9+<2"],
    },
    "unittest": {"command": "python -m unittest discover", "requires": ["mock-3+",],},
}


def commands():
    import os

    env.PATH.append(os.path.join("{root}", "bin"))
    env.PYTHONPATH.append(os.path.join("{root}", "python"))
