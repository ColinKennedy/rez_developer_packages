# -*- coding: utf-8 -*-

name = "rez_plugin"

# TODO : Replace this with a `1` major, later
version = "0.1.0"

description = "A basic CLI plug-in system for Rez."

authors = ["ColinKennedy (colinvfx@gmail.com)"]

help = [["README", "README.md"]]

requires = ["python-2.7+<3.8"]

private_build_requires = ["rez_build_helper-1.1+<2"]

build_command = "python -m rez_build_helper --items python"

tests = {
    "black_diff": {
        "command": "black --diff --check python tests",
        "requires": ["black-19"],
    },
    "black": {
        "command": "black python tests",
        "requires": ["black-19"],
        "run_on": "explicit",
    },
    "isort": {
        "command": "isort --recursive python tests",
        "requires": ["isort-5"],
        "run_on": "explicit",
    },
    "isort_check": {
        "command": "isort --check-only --diff --recursive python tests",
        "requires": ["isort-5"],
    },
    "pydocstyle": {
        # Need to disable D202 for now, until a new pydocstyle version is released
        # Reference: https://github.com/psf/black/issues/1159
        #
        "command": "pydocstyle --ignore=D213,D202,D203,D406,D407 python tests/*",
        "requires": ["pydocstyle-6"],
    },
    "pylint": {
        "command": "pylint --disable=bad-continuation python/rez_documentation_check tests",
        "requires": ["pylint-1.9+<2"],
    },
    "unittest_python_2": {
        "command": "python -m unittest discover",
        "requires": ["python-2"],
    },
    "unittest_python_3": {
        "command": "python -m unittest discover",
        "requires": ["python-3"],
    }
}

uuid = "4102b6e4-90da-456a-a7e4-849ffe485917"


def commands():
    import os

    env.PATH.append(os.path.join("{root}", "bin"))
    env.PYTHONPATH.append(os.path.join("{root}", "python"))
