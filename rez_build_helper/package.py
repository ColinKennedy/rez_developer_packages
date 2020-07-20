#!/usr/bin/env python
# -*- coding: utf-8 -*-

name = "rez_build_helper"

version = "1.5.0"

description = "Build Rez packages using Python"

authors = ["ColinKennedy"]

help = [["README", "README.md"]]

build_command = "python {root}/rezbuild.py {install}"

uuid = "168c5114-a951-4834-a744-dae1331e375e"

requires = ["python-2.7+<3.8"]

tests = {
    "black_diff": {
        "command": "black --diff --check package.py python tests",
        "requires": ["black-19.10+<20"],
    },
    "black": {
        "command": "black package.py python tests",
        "requires": ["black-19.10+<20"],
        "run_on": "explicit",
    },
    "coverage": {
        "command": (
            "coverage erase "
            "&& coverage run --parallel-mode --include=python/* -m unittest discover "
            "&& coverage combine --append "
            "&& coverage html"
        ),
        "requires": ["coverage-5.1+<6", "rez-2.47+<3", "wurlitzer-2+<3"],
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
    "pylint": {
        "command": "pylint --disable=bad-continuation python/rez_build_helper tests",
        "requires": ["pylint-1.9+<2"],
    },
    "unittest_python_2": {
        "command": "python -m unittest discover",
        "requires": ["rez-2.48+<3", "wurlitzer-2+<3"],
        "on_variants": {"type": "requires", "value": ["python-2.7"]},
    },
    "unittest_python_3": {
        "command": "python -m unittest discover",
        "requires": ["rez-2.48+<3", "wurlitzer-2+<3"],
        "on_variants": {"type": "requires", "value": ["python-3.6"]},
    },
}


def commands():
    import os

    env.PYTHONPATH.append(os.path.join("{root}", "python"))
