#!/usr/bin/env python
# -*- coding: utf-8 -*-

name = "rez_build_helper"

version = "1.9.0"

description = "Build Rez packages using Python"

authors = ["ColinKennedy"]

help = [["README", "README.md"]]

build_command = "python {root}/rezbuild.py {install}"

uuid = "168c5114-a951-4834-a744-dae1331e375e"

# requires = [
#     "python-2.7+<3.8",
#     "rez-2.71+<3",
#     "setuptools-44+<52",
#     "six-1.11+<2",
#     "whichcraft-0.6+<1",
# ]
requires = ["rez-2.71+<3", "six-1.11+<2", "whichcraft-0.6+<1"]

# ``hashed_variants`` is required if you want this to build on Windows, which
# doesn't support < in folder names
#
hashed_variants = True

variants = [
    ["python-2.7", "setuptools-44+<45"],
    ["python-3.7", "setuptools-51+<52"],
]

# TODO: Check if windows and, if so, don't include wurlitzer
_common_requires = ["rez_python_compatibility-2.6+<3", "wurlitzer-2+<3"]
_common_run_on = ["default", "pre_release"]

tests = {
    "black_diff": {
        "command": "black --diff --check package.py python tests",
        "on_variants": {
            "type": "requires",
            "value": ["python-3"],
        },
        "requires": ["black-23+<24"],
        "run_on": _common_run_on,
    },
    "black": {
        "command": "black package.py python tests",
        "on_variants": {
            "type": "requires",
            "value": ["python-3"],
        },
        "requires": ["black-23+<24"],
        "run_on": "explicit",
    },
    "isort": {
        "command": "isort --profile black package.py python tests",
        "requires": ["isort-5.11+<6"],
        "run_on": "explicit",
    },
    "isort_check": {
        "command": "isort --profile black --check-only --diff package.py python tests",
        "requires": ["isort-5.11+<6"],
        "run_on": _common_run_on,
    },
    "pydocstyle": {
        # Need to disable D202 for now, until a new pydocstyle version is released
        # Reference: https://github.com/psf/black/issues/1159
        #
        "command": "pydocstyle --ignore=D213,D202,D203,D406,D407 python tests/*",
        "requires": ["pydocstyle-6+<7"],
        "run_on": _common_run_on,
    },
    "pylint_source": {
        "command": "pylint --disable=consider-using-f-string python/rez_build_helper",
        "requires": _common_requires + ["pylint-2.17+<3"],
        "run_on": _common_run_on,
    },
    "pylint_tests": {
        "command": "pylint --disable=consider-using-f-string,duplicate-code tests",
        "requires": _common_requires + ["pylint-2.17+<3"],
        "run_on": _common_run_on,
    },
    "unittest_python_2": {
        "command": "python -m unittest discover",
        "requires": _common_requires + [".add_fake_hotl-1", "python-2.7"],
        "run_on": _common_run_on,
    },
    "unittest_python_3": {
        "command": "python -m unittest discover",
        "requires": _common_requires + [".add_fake_hotl-1", "python-3.6+<3.8"],
        "run_on": _common_run_on,
    },
}


def commands():
    import os

    env.PYTHONPATH.append(os.path.join("{root}", "python"))

    if intersects(ephemerals.get("add_fake_hotl", "0"), "1"):
        # This line is only used during unittests
        env.PATH.append(os.path.join("{root}", "fake_bin"))
