# -*- coding: utf-8 -*-

name = "sphinx_apidoc_check"

version = "1.0.0"

description = (
    "Check if the user needs to re-run ``sphinx-apidoc`` on their Python package"
)

authors = [
    "ColinKennedy (colinvfx@gmail.com)",
]

requires = [
    "Sphinx-1+<2",
    "python-2+",
    "python_compatibility-1+<2",
]

private_build_requires = [
    "rez_build_helper-1+<2",
]

build_command = "python -m rez_build_helper --items bin python"

tests = {
    "unittest": "python -m unittest discover",
    "black_diff": {"command": "rez-env black -- black --diff --check python tests"},
    "black": {"command": "rez-env black -- black python tests"},
    "coverage": {
        "command": "coverage run --parallel-mode --include=python/* -m unittest discover && coverage combine --append && coverage html",
        "requires": ["coverage"],
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
        "command": "pylint --disable=bad-continuation python/sphinx_apidoc_check tests",
        "requires": ["pylint-1.9+<2"],
    },
    "package_check": {
        "command": "rez-package-check",
        "requires": ["rez_package_check-1+<2"],
    },
    "unittest": "python -m unittest discover",
}


def commands():
    import os

    env.PATH.append(os.path.join("{root}", "bin"))
    env.PYTHONPATH.append(os.path.join("{root}", "python"))