# -*- coding: utf-8 -*-

name = "rez_industry"

version = "3.0.1"

description = "A Rez package manufacturer. It reliably modifies Rez package.py files."

help = [["README", "README.md"]]

private_build_requires = ["rez_build_helper-1+<2"]

build_command = "python -m rez_build_helper --items python"

requires = [
    "parso-0.5+<1",
    "parso_helper-1+<2",
    "python-2.7+<3.8",
    "rez-2.42+<3",
    "rez_utilities-2.3+<3",
    "six-1.13+<2",
]

tests = {
    "black_diff": {
        "command": "black --diff --check package.py python tests",
        "requires": ["black-19.10+<20"],
        "run_on": "explicit",
    },
    "black": {
        "command": "black package.py python tests",
        "requires": ["black-19.10+<20"],
        "run_on": "explicit",
    },
    "coverage": {
        "command": "coverage erase && coverage run --parallel-mode --include=python/* -m unittest discover && coverage combine --append && coverage html",
        "requires": [
            "coverage-5+<6",
            "mock-1+<4",
            "rez-2.51+<3",  # The tests use newer features than what is required by the package
        ],
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
        "command": "rez-env pydocstyle -- pydocstyle --ignore=D213,D202,D203,D406,D407,D417 python tests/*"
    },
    "pylint": {
        "command": "pylint --disable=bad-continuation,duplicate-code python/rez_industry",
        "requires": ["pylint-1.9+<2"],
    },
    "unittest_python_2": {
        "command": "python -m unittest discover",
        "requires": [
            "mock-1+<4",
            "python-2.7",
            "rez-2.51+<3",  # The tests use newer features than what is required by the package
        ],
    },
    "unittest_python_3": {
        "command": "python -m unittest discover",
        "requires": [
            "python-3.6+<3.8",
            "rez-2.51+<3",  # The tests use newer features than what is required by the package
        ],
    },
}

uuid = "91c5b238-303b-45e3-b8ac-76591f99caee"


def commands():
    import os

    env.PYTHONPATH.append(os.path.join("{root}", "python"))
