name = "rez_sphinx"

version = "1.0.0"

description = "Automate the initialization and building of Sphinx documentation."

help = [["README", "README.md"]]

private_build_requires = ["rez_build_helper-1+<2"]

requires = [
    "Sphinx-1.8+<4",
    "python-2.7+<3.8",
    "rez-2.42+<3",
    "rez_bump-1.5+<2",
    "rez_industry-3.1+<4",  # TODO : Kill this awful dependency later
    "rez_python_compatibility-2.8+<3",
    "rez_utilities-2.6+<3",
    "schema-0.7+<1",
    "six-1.15+<2",
]

variants = [["python-2", "backports.functools_lru_cache"], ["python-3"]]

build_command = "python -m rez_build_helper --items bin python"

tests = {
    "black": {
        "command": "black python tests",
        "requires": ["black-22+<23"],
        "run_on": "explicit",
    },
    "black_diff": {
        "command": "black --diff --check python tests",
        "requires": ["black-22+<23"],
    },
    "build_documentation": {
        "command": "rez_sphinx build",
        "requires": ["rez_sphinx-1.9+<2"],
    },
    "isort": {
        "command": "isort python tests",
        "requires": ["isort-5.9+<6"],
        "run_on": "explicit",
    },
    "isort_check": {
        "command": "isort --check-only --diff --recursive python tests",
        "requires": ["isort-5.9+<6"],
    },
    "pydocstyle": {
        # Need to disable D417 for now, until a new pydocstyle version is released
        #
        # Reference: https://github.com/PyCQA/pydocstyle/blob/master/docs/release_notes.rst
        #
        "command": "pydocstyle --ignore=D213,D203,D406,D407,D417 python tests/*",
        "requires": ["pydocstyle-6.1+<7"],
    },
    "pylint": {
        "command": "pylint --disable=bad-continuation python/rez_sphinx tests",
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

uuid = "bea3e936-644e-4e82-b0f1-4bec37db58cc"


def commands():
    import os

    env.PATH.append(os.path.join(root, "bin"))
    env.PYTHONPATH.append(os.path.join(root, "python"))
