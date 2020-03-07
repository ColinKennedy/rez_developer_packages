# -*- coding: utf-8 -*-

name = "rez_utilities_git"

version = "1.0.1"

description = "A collection of Rez / git functions. Mostly useful for unittests."

authors = [
    "Colin Kennedy (ColinKennedy)",
]

requires = [
    "GitPython-2.1+<3",
    "python-2",
    "rez-2.47+<3",
]

help = [
    ["README", "README.md"],
]

private_build_requires = ['rez_build_helper-1+<2']

build_command = "python -m rez_build_helper --items python"

tests = {
    "black_diff": {"command": "rez-env black-19.10+ -- black --diff --check python"},
    "black": {"command": "rez-env black-19.10+ -- black python"},
    "isort": {"command": "isort --recursive python", "requires": ["isort"]},
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

def commands():
    import os

    env.PYTHONPATH.append(os.path.join("{root}", "python"))
