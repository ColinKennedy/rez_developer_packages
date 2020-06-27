# -*- coding: utf-8 -*-

name = "rez_batch_plugins"

version = "3.0.0"

description = "Several plugins to demonstrate the use of `rez_batch_process` and its plugin system."

authors = ["Colin Kennedy (ColinKennedy)"]

help = [["README", "README.md"]]

private_build_requires = ["rez_build_helper-1+<2"]

build_command = "python -m rez_build_helper --items python"

requires = [
    "GitPython-2.1+<3",
    "move_break-3+<4",
    "python-2+<3",
    "rez-2.47+<3",
    # Later versions of rez_python_compatibility save and restore sys.argv
    # and some of this package's tests mess with sys.argv. So we need a
    # recent version of rez_python_compatibility to prevent side-effects
    #
    "rez_python_compatibility-2.2+<3",
    "rez_batch_process-1+<2",
    "rez_bump-1.0.2+<2",
    "rez_industry-1+<2",
    "rez_move_imports-1+<2",
    "rez_utilities-2+<3",
    "rez_utilities_git-1+<2",
    "six-1.13+<2",
]

tests = {
    "black_diff": {
        "command": "rez-env black -- black --diff --check package.py python tests"
    },
    "black": {
        "command": "rez-env black -- black package.py python tests",
        "run_on": "explicit",
    },
    "coverage": {
        "command": "coverage run --parallel-mode --include=python/* -m unittest discover && coverage combine --append && coverage html",
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
        "command": "rez-env pydocstyle -- pydocstyle --ignore=D213,D202,D203,D406,D407 python tests/*"
    },
    "pylint": {
        "command": "pylint --disable=bad-continuation python/rez_batch_plugins tests",
        "requires": ["pylint-1.9+<2"],
    },
    "unittest": {"command": "python -m unittest discover", "requires": ["mock-3+<4"]},
}

uuid = "a3339001-8cd9-41ef-a7cb-144eed052749"


def commands():
    import os

    env.PYTHONPATH.append(os.path.join("{root}", "python"))
    env.REZ_BATCH_PROCESS_PLUGINS.append("rez_batch_plugins.plugins.move_imports")
    env.REZ_BATCH_PROCESS_PLUGINS.append("rez_batch_plugins.plugins.yaml2py")
