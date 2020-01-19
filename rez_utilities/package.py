# -*- coding: utf-8 -*-

name = "rez_utilities"

version = "1.0.0"

description = "Helper functions / objects for working with Rez."

authors = ["Colin Kennedy (https://github.com/ColinKennedy)"]

requires = [
    "python_compatibility-1+<2",
    "rez-2.47+<3",
    "six-1.12+<2",
    "wurlitzer-2+<3",  # This package is used to make Rez builds quiet. If an alternative exists, please remove this dependency
]

private_build_requires = ["rez_build_helper-1+<2"]

build_command = "python -m rez_build_helper --items python"

tests = {
    "black_diff": {"command": "rez-env black -- black --diff --check python tests"},
    "black": {"command": "rez-env black -- black python tests"},
    "coverage": {
        "command": "coverage erase && coverage run --parallel-mode --include=python/* -m unittest discover && coverage combine --append && coverage html",
        "requires": ["coverage"],
    },
    "isort": {"command": "isort --recursive python tests", "requires": ["isort"]},
    "isort_check": {
        "command": "isort --check-only --diff --recursive python tests",
        "requires": ["isort"],
    },
    "pydocstyle": {
        # Need to disable D202 for now, until a new pydocstyle version is released
        # Reference: https://github.com/psf/black/issues/1159
        #
        "command": "rez-env pydocstyle -- pydocstyle --ignore=D213,D202,D203,D406,D407 python tests",
        "requires": ["pydocstyle"],
    },
    "pylint": {
        "command": "pylint --disable=bad-continuation python/rez_utilities tests",
        "requires": ["pylint-1.9+<2"],
    },
    "unittest": "python -m unittest discover",
}


def commands():
    import os

    env.PYTHONPATH.append(os.path.join("{root}", "python"))
