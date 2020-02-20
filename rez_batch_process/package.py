# -*- coding: utf-8 -*-

name = "rez_batch_process"

version = "0.0.4"

description = (
    "Check for Rez packages that need Sphinx documentation and automatically add it."
)

authors = ["ColinKennedy (colinvfx@gmail.com)"]

help = [["README", "README.md"]]

private_build_requires = ["rez_build_helper-1+<2"]

requires = [
    "GitPython-2+<3",
    "PyGithub-1.45+<2",  # TODO : Remove this if needed. Same with `GitPython`
    "backports.functools_lru_cache-1.6+<2",
    "github3.py-1.3+<2",
    "python_compatibility-2+<3",
    "rez-2.47+<3",
    "rez_utilities-1+<2",
    "six-1.13+<2",
]

build_command = "python -m rez_build_helper --items python"

tests = {
    "black_diff": {
        "command": "rez-env black -- black --diff --check package.py python tests"
    },
    "black": {"command": "rez-env black -- black package.py python tests"},
    "coverage": {
        "command": "coverage run --parallel-mode --include=python/* -m unittest discover && coverage combine --append && coverage html",
        "requires": [
            "coverage",
            "mock-3+<4",
            "wurlitzer-2+<3",  # Used to silence calls to `rez-release`
        ],
    },
    "isort": {
        "command": "isort --recursive package.py python tests",
        "requires": ["isort"],
    },
    "isort_check": {
        "command": "isort --check-only --diff --recursive package.py python tests",
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
        "command": "pylint --disable=bad-continuation python/rez_batch_process tests",
        "requires": ["pylint-1.9+<2"],
    },
    "unittest": {
        "command": "python -m unittest discover",
        "requires": [
            "mock-3+<4",
            "wurlitzer-2+<3",  # Used to silence calls to `rez-release`
        ],
    },
}


def commands():
    """Add the Python folder and CLI to the user's environment."""
    import os

    env.PATH.append(os.path.join("{root}", "bin"))
    env.PYTHONPATH.append(os.path.join("{root}", "python"))
