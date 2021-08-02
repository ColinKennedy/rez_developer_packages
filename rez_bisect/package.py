name = "rez_bisect"

version = "1.0.0"

description = "Like 'git bisect', but for Rez. Find which packages / versions introduced some issue."

authors = ["ColinKennedy"]

private_build_requires = ["rez_build_helper-1+<2"]

requires = ["python-2.7+<4"]

build_command = "python -m rez_build_helper --items bin python"

_test_requires = ["rez-2.93+<3"]

tests = {
    "black_diff": {
        "command": "black --diff --check package.py python tests",
        "requires": ["black-19+<21"],
    },
    "black": {
        "command": "black package.py python tests",
        "requires": ["black-19+<21"],
        "run_on": "explicit",
    },
    "isort": {
        "command": "isort package.py python tests",
        "requires": ["isort-5.9+<6"],
        "run_on": "explicit",
    },
    "isort_check": {
        "command": "isort --check-only --diff package.py python tests",
        "requires": ["isort-5.9+<6"],
    },
    "pydocstyle": {
        # Need to disable D202 for now, until a new pydocstyle version is released
        # Reference: https://github.com/psf/black/issues/1159
        #
        "command": "pydocstyle --ignore=D213,D202,D203,D406,D407 python tests/*",
        "requires": ["pydocstyle-6.1+<7"],
    },
    "pylint_source": {
        "command": "pylint --disable=bad-continuation python/rez_lint",
        "requires": ["pylint-1.9+<2"],
    },
    "pylint_tests": {
        "command": "pylint --disable=bad-continuation,duplicate-code tests",
        "requires": ["pylint-1.9+<2"],
    },
    "unittest_python_2": {
        "command": "python -m unittest discover",
        "requires": _test_requires + ["python-2"],
    },
    "unittest_python_3": {
        "command": "python -m unittest discover",
        "requires": _test_requires + ["python-3"],
    },
}


def commands():
    import os

    env.PATH.append(os.path.join(root, "bin"))
    env.PYTHONPATH.append(os.path.join(root, "python"))
