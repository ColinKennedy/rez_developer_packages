#!/usr/bin/env python
# -*- coding: utf-8 -*-

name = "rez_build_helper"

version = "1.11.3"

description = "Build Rez packages using Python"

authors = ["ColinKennedy"]

help = [["README", "README.md"]]

build_command = "python {root}/rezbuild.py {install}"

uuid = "168c5114-a951-4834-a744-dae1331e375e"

requires = [
    "python-2.7+<3.10",
    "rez-2.71+<3",
    "setuptools-41+<70",
    "six-1.11+<2",
    "whichcraft-0.6+<1",
]

# TODO: Check if windows and, if so, don't include wurlitzer
_common_requires = ["wurlitzer-2+<4"]
_common_run_on = ["default", "pre_release"]

tests = {
    "black_diff": {
        "command": "black --diff --check package.py python tests",
        "requires": ["black-23+<25"],
        "run_on": _common_run_on,
    },
    "black": {
        "command": "black package.py python tests",
        "requires": ["black-23+<25"],
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
        "requires": _common_requires + ["pylint-2.17+<4"],
        "run_on": _common_run_on,
    },
    "pylint_tests": {
        "command": "pylint --disable=consider-using-f-string,duplicate-code tests",
        "requires": _common_requires + ["pylint-2.17+<4"],
        "run_on": _common_run_on,
    },
    "unittest_python_2": {
        "command": "python -m unittest discover",
        "on_variants": {
            "type": "requires",
            "value": ["python-2"],
        },
        "requires": _common_requires + [".add_fake_hotl-1", "python-2.7"],
        "run_on": _common_run_on,
    },
    "unittest_python_3.7": {
        "command": "python -m unittest discover",
        "requires": _common_requires + [".add_fake_hotl-1", "python-3.7+<3.8"],
        "run_on": _common_run_on,
    },
    "unittest_python_3.9": {
        "command": "python -m unittest discover",
        "requires": _common_requires + [".add_fake_hotl-1", "python-3.9+<3.10"],
        "run_on": _common_run_on,
    },
}


def commands():
    import os

    env.PYTHONPATH.append(os.path.join("{root}", "python"))

    if intersects(ephemerals.get("add_fake_hotl", "0"), "1"):
        # This line is only used during unittests
        env.PATH.append(os.path.join("{root}", "fake_bin"))
