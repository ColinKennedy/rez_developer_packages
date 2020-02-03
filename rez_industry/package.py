# -*- coding: utf-8 -*-

name = "rez_industry"

version = "0.1.0"

description = "A Rez package manufacturer. It's reliably modifies Rez package.py files."

help = [
    ["README", "README.md"],
]

private_build_requires = ["rez_build_helper-1+<2"]

build_command = "python -m rez_build_helper --items python"

requires = [
    "parso-0.5+<1",
    "python-2+<3",
    "rez-2.42+<3",
    "six-1.13+<2",
]

tests = {
    "black_diff": {
        "command": "rez-env black -- black --diff --check package.py python tests"
    },
    "black": {"command": "rez-env black -- black package.py python tests"},
    "coverage": {
        "command": "coverage erase && coverage run --parallel-mode --include=python/* -m unittest discover && coverage combine --append && coverage html",
        "requires": [
            "coverage-4+<5",
            "rez-2.52.1+<3",  # The tests use newer features than what is required by the package
        ],
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
        "command": "pylint --disable=bad-continuation python/rez_industry",
        "requires": ["pylint-1.9+<2"],
    },
    "unittest": {
        "command": "python -m unittest discover",
        "requires": [
            "rez-2.52.1+<3",  # The tests use newer features than what is required by the package
        ],
    },
}


def commands():
    import os

    env.PYTHONPATH.append(os.path.join("{root}", "python"))
