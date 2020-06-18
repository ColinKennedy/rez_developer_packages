# -*- coding: utf-8 -*-

name = "rez_utilities"

version = "2.0.0"

description = "Helper functions / objects for working with Rez."

authors = ["Colin Kennedy (https://github.com/ColinKennedy)"]

help = [
    ["README", "README.md"],
]

requires = [
    "python-2+<3",
    "rez-2.47+<3",
    "rez_python_compatibility-2+<3",
    "six-1.12+<2",
    "wurlitzer-2+<3",  # This package is used to make Rez builds quiet. If an alternative exists, please remove this dependency
]

private_build_requires = ["rez_build_helper-1+<2"]

build_command = "python -m rez_build_helper --items python"

tests = {
    "black_diff": {"command": "rez-env black-19.10+ -- black --diff --check python tests"},
    "black": {"command": "rez-env black-18+ -- black python tests"},
    "coverage": {
        "command": "coverage erase && coverage run --parallel-mode --include=python/* -m unittest discover && coverage combine --append && coverage html",
        "requires": [
            "GitPython-2+<4",
            "coverage-4.5+<5",
            "mock-3+<4",
        ],
    },
    "isort": {"command": "isort --recursive python tests", "requires": ["isort"]},
    "isort_check": {
        "command": "isort --check-only --diff --recursive python tests",
        "requires": ["isort-4.3+<5"],
    },
    "pydocstyle": {
        # Need to disable D202 for now, until a new pydocstyle version is released
        # Reference: https://github.com/psf/black/issues/1159
        #
        "command": "pydocstyle --ignore=D213,D202,D203,D406,D407 python tests/*",
        "requires": ["pydocstyle-3+"],
    },
    "pylint_source": {
        "command": "pylint --disable=bad-continuation python/rez_utilities",
        "requires": [
            "pylint-1.9+<2",
        ],
    },
    "pylint_tests": {
        "command": "pylint --disable=bad-continuation,duplicate-code tests",
        "requires": [
            "GitPython-2+<4",
            "pylint-1.9+<2",
        ],
    },
    "unittest": {
        "command": "python -m unittest discover",
        "requires": [
            "GitPython-2+<4",
            "mock-3+<4",
        ],
    },
}


def commands():
    import os

    env.PYTHONPATH.append(os.path.join("{root}", "python"))
