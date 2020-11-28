# -*- coding: utf-8 -*-

name = "parso_helper"

version = "1.2.0"

description = "Functions that make using parso a bit easier"

authors = [
    "Colin Kennedy (ColinKennedy)",
]

private_build_requires = ["rez_build_helper-1+<2"]

requires = ["parso-0.5+<1", "python-2+<3.8"]

build_command = "python -m rez_build_helper --items python"

uuid = "c989f6ef-7f52-4acf-8660-e0268049f700"

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
        "command": "pydocstyle --ignore=D213,D202,D203,D406,D407 python tests/*",
        "requires": ["pydocstyle-3+<5"],
    },
    "pylint": {
        "command": "pylint --disable=bad-continuation python/move_break tests",
        "requires": ["pylint-1.9+<2"],
    },
    "unittest_python_2": {
        "command": "python -m unittest discover",
        "requires": ["python-2"],
    },
    "unittest_python_3": {
        "command": "python -m unittest discover",
        "requires": ["python-3.6+<3.8"],
    },
}


def commands():
    import os

    env.PYTHONPATH.append(os.path.join("{root}", "python"))
