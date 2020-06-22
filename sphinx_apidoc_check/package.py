# -*- coding: utf-8 -*-

name = "sphinx_apidoc_check"

version = "1.3.0"

description = (
    "Check if the user needs to re-run ``sphinx-apidoc`` on their Python package"
)

authors = [
    "ColinKennedy (colinvfx@gmail.com)",
]

help = [
    ["README", "README.md"],
]

requires = [
    "Sphinx-1+<2",
    "python-2+",
    "rez_python_compatibility-2+<3",
]

private_build_requires = [
    "rez_build_helper-1+<2",
]

build_command = "python -m rez_build_helper --items bin python"

tests = {
    "black_diff": {"command": "rez-env black -- black --diff --check python tests"},
    "black": {
        "command": "rez-env black -- black python tests",
        "run_on": "explicit",
    },
    "coverage": {
        "command": "coverage run --parallel-mode --include=python/* -m unittest discover && coverage combine --append && coverage html",
        "requires": ["coverage-4+"],
        "run_on": "explicit",
    },
    "isort": {"command": "isort --recursive python tests", "requires": ["isort"]},
    "isort_check": {
        "command": "isort --check-only --diff --recursive python tests",
        "requires": ["isort"],
        "run_on": "explicit",
    },
    "pydocstyle": {
        # Need to disable D202 for now, until a new pydocstyle version is released
        # Reference: https://github.com/psf/black/issues/1159
        #
        # TODO : Why does the tests folder not get picked up?
        "command": "rez-env pydocstyle -- pydocstyle --ignore=D213,D202,D203,D406,D407 python tests",
        "requires": ["pydocstyle"],
    },
    "pylint": {
        "command": "pylint --disable=bad-continuation python/sphinx_apidoc_check tests",
        "requires": ["pylint-1.9+<2"],
    },
    "unittest": "python -m unittest discover",
    "rez_lint": {
        "command": "rez_lint",
        "requires": [
            "rez_lint-1+<2",
        ],
    },
}

uuid = "5dda65f8-776f-44ea-bf2f-1e610a18bf01"


def commands():
    import os

    env.PATH.append(os.path.join("{root}", "bin"))
    env.PYTHONPATH.append(os.path.join("{root}", "python"))
