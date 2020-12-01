# -*- coding: utf-8 -*-

name = "rez_test_env"

version = "1.0.0"

description = "A small CLI for making a Rez environment + tests really easy to do."

help = [["README", "README.md"]]

authors = ["ColinKennedy"]

private_build_requires = ["rez_build_helper-1+<2"]

requires = ["python-2+<3.8", "rez-2.50+<3"]

build_command = "python -m rez_build_helper --items bin python"

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
    "coverage": {
        "command": (
            "coverage erase "
            "&& coverage run --parallel-mode --include=python/* -m unittest discover "
            "&& coverage combine --append "
            "&& coverage html"
        ),
        "requires": ["coverage-4+<5", "rez_utilities-2+<3", "wurlitzer-2+<3"],
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
        "command": "rez-env pydocstyle-3.0 -- pydocstyle --ignore=D213,D202,D203,D406,D407 python tests/*",
    },
    "pylint": {
        "command": "pylint --disable=bad-continuation python/rez_test_env tests",
        "requires": ["pylint-1.9+<2", "rez_utilities-2+<3", "wurlitzer-2+<3"],
    },
    "unittest": {
        "command": "python -m unittest discover",
        "requires": ["rez_utilities-2+<3", "wurlitzer-2+<3"],
    },
}

uuid = "61969a5b-5709-4504-b2ac-db755b438618"


def commands():
    import os

    env.PATH.append(os.path.join("{root}", "bin"))
    env.PYTHONPATH.append(os.path.join("{root}", "python"))
