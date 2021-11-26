name = "rez_docbot"

version = "1.0.0"

description = "Auto build, link, and publish documentation, via Rez"

authors = ["ColinKennedy"]

build_command = "python -m rez_build_helper --items bin python"

private_build_requires = ["rez_build_helper-1.8+<2"]

requires = [
    "Sphinx-1.8+<2",
    "six-1.16+<2",
]

tests = {
    "black_diff": {
        "command": "black --diff --check package.py python tests",
        "requires": ["black-11+<12"],  # TODO : Double-check version
    },
    "black": {
        "command": "black package.py python tests",
        "requires": ["black-11+<12"],  # TODO : Double-check version
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
        "command": "pydocstyle --ignore=D213,D202,D203,D406,D407 python tests",  # TODO : Double-check the ignores
        "requires": ["pydocstyle-4+<5"],  # TODO : Double-check version number. Should be python-3 enabled

    },
    "pylint": {
        "command": "pylint --disable=bad-continuation python/rez_docbot tests",
        "requires": ["pylint-1.9+<2"],
    },
    "unittest_python_2": {
        "command": "python -m unittest discover",
        "requires": ["python-2"],
    },
    "unittest_python_3": {
        "command": "python -m unittest discover",
        "requires": ["python-3"],
    },
}


def commands():
    import os

    env.PATH.append(os.path.join(root, "bin"))
    env.PYTHONPATH.append(os.path.join(root, "python"))
