# -*- coding: utf-8 -*-

name = "move_break"

version = "1.1.1"

description = "Change, replace, and move Python imports"

authors = ["Colin Kennedy (ColinKennedy)"]

private_build_requires = ["rez_build_helper-1+<2"]

requires = [
    "parso-0.5+<1",
    "parso_helper-1+<2",
    "python-2",
    "python_compatibility-2+<3",
    "six-1.12+<2",
]

tests = {
    "black_diff": {
        "command": "rez-env black -- black --diff --check package.py python tests"
    },
    "black": {"command": "rez-env black -- black package.py python tests"},
    "coverage": {
        "command": "coverage run --parallel-mode --include=python/* -m unittest discover && coverage combine --append && coverage html",
        "requires": ["coverage"],
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
        "command": "rez-env pydocstyle -- pydocstyle --ignore=D213,D202,D203,D406,D407 python tests/*",
        "requires": ["pydocstyle"],
    },
    "pylint": {
        "command": "pylint --disable=bad-continuation python/move_break tests",
        "requires": ["pylint-1.9+<2"],
    },
    "unittest": "python -m unittest discover",
}

build_command = "python -m rez_build_helper --items python"


def commands():
    import os

    env.PYTHONPATH.append(os.path.join("{root}", "python"))
