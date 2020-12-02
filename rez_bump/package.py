# -*- coding: utf-8 -*-

name = "rez_bump"

version = "1.5.0"

description = "Control the version value of Rez packages"

authors = ["Colin Kennedy (ColinKennedy)"]

requires = [
    "parso-0.6+<1",
    "python-2+<3.8",
    "rez-2.42+<3",
    "rez_industry-1+<3",
    "rez_utilities-2+<3",
]

help = [["README", "README.md"]]

private_build_requires = ["rez_build_helper-1+<2"]

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
        "command": "coverage erase && coverage run --parallel-mode --include=python/* -m unittest discover && coverage combine --append && coverage html",
        "requires": ["coverage-4+<5"],
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
    "pylint": {
        "command": "pylint --disable=bad-continuation python/rez_bump",
        "requires": ["pylint-1.9+<2"],
    },
    "unittest_python_2": {
        "command": "python -m unittest discover",
        "requires": ["python-2.7"],
    },
    "unittest_python_3": {
        "command": "python -m unittest discover",
        "requires": ["python-3.6+<3.8"],
    },
}

uuid = "e96d5484-abd7-49d4-a0e7-95d7b5540272"


def commands():
    import os

    env.PYTHONPATH.append(os.path.join("{root}", "python"))
