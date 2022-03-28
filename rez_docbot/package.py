# TODO : Consider making this a "non-Rez" name. Does it really have any Rez
# components? Maybe not.
#
name = "rez_docbot"

version = "1.0.0"

authors = ["ColinKennedy"]

private_build_requires = ["rez_build_helper-1+<2"]

requires = [
    "python-2+<4",
    "rez_python_compatibility-2.7+<3",
    "schema-0.7+<1",
    "six-1.15+<2",
]

build_command = "python -m rez_build_helper --items python"

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
    # TODO : Add configuration files for these changes. And isort and pydocstyle
    "pylint": {
        "command": "pylint --disable=use-dict-literal,use-list-literal,bad-continuation,consider-using-f-string,super-with-arguments,useless-object-inheritance,raise-missing-from python/rez_docbot tests",
        "requires": ["pylint-2.12+<3"],
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

    env.PYTHONPATH.append(os.path.join(root, "python"))
