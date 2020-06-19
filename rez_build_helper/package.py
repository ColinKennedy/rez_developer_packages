#!/usr/bin/env python
# -*- coding: utf-8 -*-

name = "rez_build_helper"

version = "1.4.0"

description = "Build Rez packages using Python"

authors = ["ColinKennedy"]

help = [
    ["README", "README.md"],
]

build_command = 'python {root}/rezbuild.py {install}'

uuid = "168c5114-a951-4834-a744-dae1331e375e"

tests = {
    "black_diff": {
        "command": "rez-env black -- black --diff --check package.py python tests"
    },
    "black": {
        "command": "rez-env black -- black package.py python tests",
        "run_on": "explicit",
    },
    "coverage": {
        "command": "coverage run --parallel-mode --include=python/* -m unittest discover && coverage combine --append && coverage html",
        "requires": ["coverage"],
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
    "unittest": {
        "command": "python -m unittest discover",
        "requires": [
            "rez_python_compatibility-2.3+<3",
            "rez_utilities-2+<3",
        ],
    },
}

def commands():
    import os

    env.PYTHONPATH.append(os.path.join("{root}", "python"))
