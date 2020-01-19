# -*- coding: utf-8 -*-

name = "rez_documentation_check"

version = "0.0.8"

description = "Check a Rez package's Sphinx documentation for issues"

authors = ["ColinKennedy (colinvfx@gmail.com)"]

requires = [
    "parso-0.5+<1",
    "python_compatibility-1+<2",
    "rez-2.47+<3",
    "rez_utilities-1+<2",
    "six-1.13+<2",
    "wurlitzer-2+<3",
]

private_build_requires = ["rez_build_helper-1.1+<2"]

variants = [["python-2.7"]]

build_command = "python -m rez_build_helper --items bin python"

tests = {
    "black_diff": {"command": "rez-env black -- black --diff --check python tests"},
    "black": {"command": "rez-env black -- black python tests"},
    "coverage": {
        "command": "coverage run --parallel-mode --include=python/* -m unittest discover && coverage combine --append && coverage html",
        "requires": ["coverage"],
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
        "command": "pylint --disable=bad-continuation python/rez_documentation_check tests",
        "requires": ["pylint-1.9+<2"],
    },
    "package_check": {
        "command": "rez-package-check",
        "requires": ["rez_package_check-1+<2"],
    },
    "unittest": {
        "command": "python -m unittest discover",
        "requires": [
            "mock-3+<4",
        ],
    }
}


def commands():
    """Add the Python folder and CLI to the user's environment."""
    import os

    env.PATH.append(os.path.join("{root}", "bin"))
    env.PYTHONPATH.append(os.path.join("{root}", "python"))
