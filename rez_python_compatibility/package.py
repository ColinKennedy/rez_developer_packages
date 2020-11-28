# -*- coding: utf-8 -*-

name = "rez_python_compatibility"

version = "2.4.1"

description = "Miscellaneous, core Python 2 + 3 functions."

authors = ["Colin Kennedy (https://github.com/ColinKennedy)"]

help = [
    ["README", "README.md"],
]

requires = [
    "backports.tempfile-1+<2",
    "six-1.13+<2",
]

private_build_requires = ["rez_build_helper-1.1+<2"]

build_command = "python -m rez_build_helper --items python"

variants = [["python-2.7"], ["python-3"]]

tests = {
    "black_diff": {
        "command": "black --diff --check python tests",
        "requires": ["black-19.10+<21"],
    },
    "black": {
        "command": "rez-env black-19.10+ -- black python tests",
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
        "requires": ["coverage-4.5+"],
        "run_on": "explicit",
    },
    "isort": {
        "command": "isort --recursive python tests",
        "requires": ["isort-4.3+<5"],
        "run_on": "explicit",
    },
    "isort_check": {
        "command": "isort --check-only --diff --recursive python tests",
        "requires": ["isort-4.3+<5"],
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
    "unittest_python_2": {
        "command": "python -m unittest discover",
        "requires": ["python-2.7"],
    },
    "unittest_python_3": {
        "command": "python -m unittest discover",
        "requires": ["python-3.6+<3.8"],
    },
}

uuid = "efb980ba-9580-4c60-b47f-fa0c7ebdabf4"


def commands():
    import os

    env.PYTHONPATH.append(os.path.join("{root}", "python"))
