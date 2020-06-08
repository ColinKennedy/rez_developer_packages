# -*- coding: utf-8 -*-

name = "rez_move_imports"

version = "1.3.0"

description = "Change a Rez package's imports and then bump the require Rez version(s)"

authors = ["Colin Kennedy (ColinKennedy)"]

help = [["README", "README.md"]]

private_build_requires = ["rez_build_helper-1+<2"]

requires = [
    "move_break-3+<4",
    "python-2+<3",
    "python_compatibility-2.3+<3",
    "rez-2.42+<3",
    "rez_bump-1.1+<2",
    "rez_industry-1+<2",
    "rez_utilities-1.4+<2",
]

build_command = "python -m rez_build_helper --items python"

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
        "requires": ["coverage-5+<6"],
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
        "command": "rez-env pydocstyle -- pydocstyle --ignore=D213,D202,D203,D406,D407 python tests/*"
    },
    "pylint": {
        "command": "pylint --disable=bad-continuation python/rez_move_imports tests",
        "requires": ["pylint-1.9+<2"],
    },
    "unittest": "python -m unittest discover",
}


def commands():
    import os

    env.PYTHONPATH.append(os.path.join("{root}", "python"))
