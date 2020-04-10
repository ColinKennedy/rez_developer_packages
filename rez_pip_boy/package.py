name = "rez_pip_boy"

version = "1.0.0"

description = "Convert an installed pip package back into a source package"

authors = [
    "Colin Kennedy",
]

help = [["README", "README.md"]]

private_build_requires = ["rez_build_helper-1+<2"]

build_command = "python -m rez_build_helper --items bin python"

requires = [
    "python-2+<3",
    "rez-2.47+<3",
    "rez_utilities-1.4+<2",
    "six-1.14+<2",
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
        "command": "rez-env pydocstyle -- pydocstyle --ignore=D202,D203,D213,D406,D407 python tests/*"
    },
    "pylint": {
        "command": "pylint --disable=bad-continuation python/rez_pip_boy tests",
        "requires": ["pylint-1.9+<2"],
    },
    "unittest": {"command": "python -m unittest discover"},
}


def commands():
    import os

    env.PATH.append(os.path.join("{root}", "bin"))
    env.PYTHONPATH.append(os.path.join("{root}", "python"))
