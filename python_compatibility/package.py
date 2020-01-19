# -*- coding: utf-8 -*-

name = "python_compatibility"

version = "1.0.0"

description = "Miscellaneous, core Python 2 + 3 functions."

authors = ["Colin Kennedy (https://github.com/ColinKennedy)"]

requires = [
    "backports.tempfile-1+<2",
    "six-1.13+<2",
]

private_build_requires = ["rez_build_helper-1.1+<2"]

variants = [["python-2.7"]]

build_command = "python -m rez_build_helper --items bin python"

tests = {
    "black_diff": {"command": "rez-env black-19.10+ -- black --diff --check python tests"},
    "black": {"command": "rez-env black-19.10+ -- black python tests"},
    "coverage": {
        "command": "coverage run --parallel-mode --include=python/* -m unittest discover && coverage combine --append && coverage html",
        "requires": ["coverage-4.5+"],
    },
    "isort": {"command": "isort --recursive python tests", "requires": ["isort"]},
    "isort_check": {
        "command": "isort --check-only --diff --recursive python tests",
        "requires": ["isort-4.3+"],
    },
    "pydocstyle": {
        # Need to disable D202 for now, until a new pydocstyle version is released
        # Reference: https://github.com/psf/black/issues/1159
        #
        "command": "pydocstyle --ignore=D213,D202,D203,D406,D407 python tests",
        "requires": ["pydocstyle-3+"],
    },
    "pylint": {
        "command": "pylint --disable=bad-continuation python/python_compatibility tests",
        "requires": ["pylint-1.9+<2"],
    },
    "unittest": "python -m unittest discover",
}


def commands():
    import os

    env.PATH.append(os.path.join("{root}", "bin"))
    env.PYTHONPATH.append(os.path.join("{root}", "python"))
    env.PYTHON_COMPATIBILITY_DEPENDENCY_PATHS_SCRIPT.set("_get-python-dependency-paths")
