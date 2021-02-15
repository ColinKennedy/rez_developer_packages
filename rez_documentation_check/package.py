# -*- coding: utf-8 -*-

name = "rez_documentation_check"

version = "0.5.0"

description = "Check a Rez package's Sphinx documentation for issues"

authors = ["ColinKennedy (colinvfx@gmail.com)"]

help = [
    ["README", "README.md"],
]

requires = [
    "parso-0.5+<1",
    "python-2.7+<3.8",
    "rez-2.47+<3",
    "rez_python_compatibility-2+<3",
    "rez_utilities-2+<3",
    "six-1.13+<2",
]

private_build_requires = ["rez_build_helper-1.1+<2"]

build_command = "python -m rez_build_helper --items bin python"

tests = {
    "black_diff": {
        "command": "rez-env black -- black --diff --check python tests",
    },
    "black": {
        "command": "rez-env black -- black python tests",
        "run_on": "explicit",
    },
    "coverage": {
        "command": "coverage run --parallel-mode --include=python/* -m unittest discover && coverage combine --append && coverage html",
        "requires": [
            "coverage-4.5+<5",
            "mock-3+<4",
            "wurlitzer-2+<3",
        ],
    },
    "documentation_api": {
        "command": "rm -rf documentation/source/api && sphinx-apidoc python --module-first --separate --o documentation/source/api",
        "requires": [
            "Sphinx-1.8+<2",
        ],
    },
    "documentation_build": {
        "command": "sphinx-build documentation/source documentation/build",
        "requires": [
            "Sphinx-1.8+<2",
        ],
    },
    "documentation_check_links": {
        "command": "sphinx-build -b linkcheck documentation/source documentation/build",
        "requires": [
            "Sphinx-1.8+<2",
        ],
    },
    "isort": {
        "command": "isort --recursive python tests",
        "requires": ["isort"],
        "run_on": "explicit",
    },
    "isort_check": {
        "command": "isort --check-only --diff --recursive python tests",
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
        "command": "pylint --disable=bad-continuation python/rez_documentation_check tests",
        "requires": ["pylint-1.9+<2"],
    },
    "unittest_python_2": {
        "command": "python -m unittest discover",
        "requires": ["mock-3+<4", "python-2.7", "wurlitzer-2+<3"],
    },
    "unittest_python_3": {
        "command": "python -m unittest discover",
        "requires": ["python-3+", "wurlitzer-2+<3"],
    }
}

uuid = "c11e8439-d5f4-4e48-8002-5831cff647d9"


def commands():
    """Add the Python folder and CLI to the user's environment."""
    import os

    env.PATH.append(os.path.join("{root}", "bin"))
    env.PYTHONPATH.append(os.path.join("{root}", "python"))
