# -*- coding: utf-8 -*-

name = "rez_python_compatibility"

version = "2.9.2"

description = "Miscellaneous, core Python 2 + 3 functions."

authors = ["Colin Kennedy (https://github.com/ColinKennedy)"]

help = [
    ["README", "README.md"],
]

requires = ["mock-3+<6", "python-2.7+<3.10", "six-1.13+<2"]

private_build_requires = ["python-2", "rez_build_helper-1.1+<2"]

build_command = "python -m rez_build_helper --items python"

_common_run_on = ["default", "pre_release"]

tests = {
    "black_diff": {
        "command": "black --diff --check python tests",
        "requires": ["black-23+<25"],
        "run_on": _common_run_on,
    },
    "black": {
        "command": "black python tests",
        "requires": ["black-23+<25"],
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
        "command": "isort --profile black python tests",
        "requires": ["isort-5.11+<6"],
        "run_on": "explicit",
    },
    "isort_check": {
        "command": "isort --profile black --check-only --diff python tests",
        "requires": ["isort-5.11+<6"],
        "run_on": _common_run_on,
    },
    "pydocstyle": {
        # Need to disable D202 for now, until a new pydocstyle version is released
        # Reference: https://github.com/psf/black/issues/1159
        #
        "command": "pydocstyle --ignore=D213,D202,D203,D406,D407 python tests",
        "requires": ["pydocstyle-6+<7"],
        "run_on": _common_run_on,
    },
    "pylint": {
        # TODO: These --disable flags require deprecating Python 2. Once Python
        # 2 is deprecated, add the flags back in.
        #
        "command": "pylint --disable=super-with-arguments,useless-object-inheritance,consider-using-f-string,raise-missing-from,consider-using-assignment-expr python/python_compatibility tests",
        "requires": ["pylint-2.17+<4"],
        "run_on": _common_run_on,
    },
    "unittest_python_2": {
        "command": "python -m unittest discover",
        "requires": ["python-2.7"],
        "run_on": _common_run_on,
    },
    "unittest_python_3.9": {
        "command": "python -m unittest discover",
        "requires": ["python-3.9"],
        "run_on": _common_run_on,
    },
}

uuid = "efb980ba-9580-4c60-b47f-fa0c7ebdabf4"


def commands():
    import os

    env.PYTHONPATH.append(os.path.join("{root}", "python"))
