name = "qt_rez_core"

version = "1.0.0"

description = "A set of developer tools which ease writing hybrid Qt/Rez functions."

authors = ["ColinKennedy"]

help = [["README", "README.rst"]]

private_build_requires = ["rez_build_helper-1+<2"]

build_command = "python -m rez_build_helper --items python"

@late()
def requires():
    output = [
        "Qt.py-1.3+<2",
        "python-2.7+<4",
        "rez-2.106+<3",
        "rez_utilities-2.7+<3",
        "six-1.16+<2",
    ]

    if not in_context():
        return output

    if "PySide" in request:
        output += ["PySide-1.2+<2"]
    elif "PySide2" in request:
        output += ["PySide2-5.15+<6"]
    elif "PyQt5" in request:
        output += ["PyQt5-5.15+<6"]
    else:
        output += ["PySide2-5.15+<6"]

    return output

tests = {
    "black": {
        "command": "black python tests",
        "requires": ["black-22.3+<23"],
        "run_on": "explicit",
    },
    "black_diff": {
        "command": "black --diff --check python tests",
        "requires": ["black-22.3+<23"],
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
    # TODO : Remove "fixme", later
    "pylint": {
        "command": "pylint --disable=use-dict-literal,use-list-literal,bad-continuation,consider-using-f-string,super-with-arguments,useless-object-inheritance,raise-missing-from,fixme python/qt_rez_core tests",
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
