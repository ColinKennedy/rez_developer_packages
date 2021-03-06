# -*- coding: utf-8 -*-

name = "rez_utilities_git"

version = "1.1.0"

description = "A collection of Rez / git functions. Mostly useful for unittests."

authors = [
    "Colin Kennedy (ColinKennedy)",
]

requires = [
    "GitPython-2.1+<3",
    "python-2",
    "rez-2.47+<3",
    "rez_utilities-2+<3",
]

help = [
    ["README", "README.md"],
]

private_build_requires = ['rez_build_helper-1+<2']

build_command = "python -m rez_build_helper --items python"

tests = {
    "black_diff": {"command": "rez-env black-19.10+ -- black --diff --check python"},
    "black": {
        "command": "rez-env black-19.10+ -- black python",
        "run_on": "explicit",
    },
    "isort": {
        "command": "isort --recursive python",
        "requires": ["isort"],
        "run_on": "explicit",
    },
    "isort_check": {
        "command": "isort --check-only --diff --recursive python",
        "requires": ["isort-4.3+<5"],
    },
    "pydocstyle": {
        # Need to disable D202 for now, until a new pydocstyle version is released
        # Reference: https://github.com/psf/black/issues/1159
        #
        "command": "pydocstyle --ignore=D213,D202,D203,D406,D407 python",
        "requires": ["pydocstyle-3+"],
    },
    "pylint": {
        "command": "pylint --disable=bad-continuation python/rez_utilities_git",
        "requires": [
            "GitPython-2+<4",
            "pylint-1.9+<2",
        ],
    },
}

uuid = "fb9ac0e1-8c1f-401b-8cf0-54831331e138"


def commands():
    import os

    env.PYTHONPATH.append(os.path.join("{root}", "python"))
