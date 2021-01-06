#!/usr/bin/env python
# -*- coding: utf-8 -*-

name = "rez_build_helper"

version = "1.7.0"

description = "Build Rez packages using Python"

authors = ["ColinKennedy"]

help = [["README", "README.md"]]

build_command = "python {root}/rezbuild.py {install}"

uuid = "168c5114-a951-4834-a744-dae1331e375e"

requires = ["rez-2.48+<3", "six-1.11+<2"]

variants = [
    ["python-2.7", "setuptools-44+<45"],
    ["python-3.6", "setuptools-51+<52"],
]

tests = {
    "black_diff": {
        "command": "black --diff --check package.py python tests",
        "requires": ["black-19.10+<21"],
    },
    "black": {
        "command": "black package.py python tests",
        "requires": ["black-19.10+<21"],
        "run_on": "explicit",
    },
    "isort": {
        "command": "isort --recursive package.py python tests",
        "requires": ["isort-4.3+<5"],
        "run_on": "explicit",
    },
    "isort_check": {
        "command": "isort --check-only --diff --recursive package.py python tests",
        "requires": ["isort-4.3+<5"],
    },
    "pydocstyle": {
        # Need to disable D202 for now, until a new pydocstyle version is released
        # Reference: https://github.com/psf/black/issues/1159
        #
        "command": "rez-env pydocstyle==3.0.0 -- pydocstyle --ignore=D213,D202,D203,D406,D407 python tests/*",
    },
    "pylint_source": {
        "command": "pylint --disable=bad-continuation python/rez_build_helper",
        "requires": ["pylint-1.9+<2", "wurlitzer-2+<3"],
    },
    "pylint_tests": {
        "command": "pylint --disable=bad-continuation,duplicate-code tests",
        "requires": [
            "pylint-1.9+<2",
            "rez_python_compatibility-2.6+<3",
            "wurlitzer-2+<3",
        ],
    },
    "unittest_python_2": {
        "command": "python -m unittest discover",
        "requires": [
            "python-2.7",
            "rez-2.48+<3",
            "rez_python_compatibility-2.6+<3",
            "wurlitzer-2+<3",
        ],
    },
    "unittest_python_3": {
        "command": "python -m unittest discover",
        "requires": [
            "python-3.6+<3.8",
            "rez-2.48+<3",
            "rez_python_compatibility-2.6+<3",
            "wurlitzer-2+<3",
        ],
    },
}


def commands():
    import os

    env.PYTHONPATH.append(os.path.join("{root}", "python"))
