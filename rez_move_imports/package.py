# -*- coding: utf-8 -*-

name = "rez_move_imports"

version = "1.8.0"

description = "Change a Rez package's imports and then bump the require Rez version(s)"

authors = ["Colin Kennedy (ColinKennedy)"]

help = [["README", "README.md"]]

private_build_requires = ["rez_build_helper-1+<2"]

requires = [
    "move_break-3+<4",
    "python-2+<3.8",
    "rez-2.42+<3",
    "rez_bump-1.1+<2",
    "rez_industry-2+<4",
    "rez_python_compatibility-2.3+<3",
    "rez_utilities-2+<3",
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
        "command": "rez-env pydocstyle -- pydocstyle --ignore=D213,D202,D203,D406,D407 python tests/*"
    },
    "pylint_source": {
        "command": "pylint --disable=bad-continuation python/rez_move_imports",
        "requires": ["pylint-1.9+<2"],
    },
    "pylint_tests": {
        "command": "pylint --disable=bad-continuation,duplicate-code tests",
        "requires": ["pylint-1.9+<2"],
    },
    "unittest_python_2": {
        "command": "python -m unittest discover",
        "requires": [
            "python-2.7",
            "rez-2.53+<3",  # Needs to support `"run_on": "explicit"`
        ],
    },
    "unittest_python_3": {
        "command": "python -m unittest discover",
        "requires": [
            "python-3.6+",
            "rez-2.53+<3",  # Needs to support `"run_on": "explicit"`
        ],
    },
}

uuid = "5bfaee62-4aa3-4311-b50e-6b3844c6ef1b"


def commands():
    import os

    env.PYTHONPATH.append(os.path.join("{root}", "python"))
