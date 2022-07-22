name = "rez_bisect"

version = "1.0.0"

description = "Like 'git bisect', but for Rez. Find which packages / versions introduced some issue."

authors = ["ColinKennedy"]

private_build_requires = ["rez_build_helper-1+<2"]

requires = [
    "python-2.7+<4",
    "rez-issues-1275-diff_packages_path_fix",  # 2.106+<2.110",  # TODO : Consider relaxing this once it's confirmed working
]

build_command = "python -m rez_build_helper --items bin python"

_test_requires = ["rez_python_compatibility-2.8+<3", "six-1.16+<2"]

tests = {
    "black_diff": {
        "command": "black --diff --check package.py python tests",
        "requires": ["black-22.1+<23"],
    },
    "black": {
        "command": "black package.py python tests",
        "requires": ["black-22.1+<23"],
        "run_on": "explicit",
    },
    "isort": {
        "command": "isort package.py python tests",
        "requires": ["isort-5.10+<6"],
        "run_on": "explicit",
    },
    "isort_check": {
        "command": "isort --check-only --diff package.py python tests",
        "requires": ["isort-5.10+<6"],
    },
    "pydocstyle": {
        # Need to disable D417 for now, until a new pydocstyle version is released
        #
        # Reference: https://github.com/PyCQA/pydocstyle/blob/master/docs/release_notes.rst
        #
        # Need to disable D202 for now, until a new pydocstyle version is released
        # Reference: https://github.com/psf/black/issues/1159
        #
        "command": "pydocstyle --ignore=D213,D202,D203,D406,D407,D417 python tests/*",
        "requires": ["pydocstyle-6.1+<7"],
    },
    "pylint": {
        "command": "pylint --disable=bad-continuation python/rez_bisect",
        "requires": ["pylint-2.12+<3"],
    },
    "unittest_python_2": {
        "command": "python -m unittest discover",
        "requires": _test_requires + ["mock-3+<4", "python-2"],
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
