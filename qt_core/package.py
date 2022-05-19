name = "qt_core"

version = "1.0.0"

description = "Extra classes and functions for making Qt easier to use."

authors = ["ColinKennedy"]

uuid = "core.qt.simple"


@late()
def requires():
    output = ["Qt.py-1.3+<2", "python-2.7+<4"]

    if not in_context():
        return output

    if "PySide2" in request:
        output += ["PySide2-5.15+<6"]
    elif "PyQt5" in request:
        output += ["PySide2-5.15+<6"]
    elif "PySide" in request:
        output += ["PySide-1.2+<2"]
    # TODO : Add this later
    # elif "PyQt4" in request:
    #     output += ["PyQt4-4.11+<5"]

    return output

private_build_requires = ["rez_build_helper-1.8+<2"]

build_command = "python -m rez_build_helper --egg python"

tests = {
    "black_diff": {
        "command": "black --diff --check python tests",
        "requires": ["black-22.3+<23"],
    },
    "black": {
        "command": "black python tests",
        "requires": ["black-22.3+<23"],
        "run_on": "explicit",
    },
    "isort": {
        "command": "isort_black python tests",
        "requires": ["isort_black-1"],
        "run_on": "explicit",
    },
    "isort_check": {
        "command": "isort_black --check-only --diff python tests",
        "requires": ["isort_black-1"],
    },
    "pydocstyle": {
        # Need to disable D202 for now, until a new pydocstyle version is released
        #
        # Reference: https://github.com/psf/black/issues/1159
        #
        # Need to display D417 for now, until a new pydocstyle version is released
        #
        # Reference: https://github.com/PyCQA/pydocstyle/issues/449
        #
        "command": "pydocstyle --ignore=D213,D202,D203,D406,D407,D417 python tests/*",
        "requires": ["pydocstyle-6+<7"],
    },
    "pylint": {
        # We need to temporarily disable features that are either Python-3-only
        # or are otherwise unsupported by other CI linters in our tests.
        #
        # bad-continuation:
        #     black creates these - however black is right and pylint is wrong
        # raise-missing-from:
        #     A Python-3-only feature. Though we should raise ... from ... once
        #     we drop Python 2 support.
        # consider-using-f-string:
        #     A Python-3-only feature. Though we should use them wherever
        #     possible once we drop Python 2 support.
        # super-with-arguments:
        #     A Python-3-only feature. Though we should use them wherever
        #     possible once we drop Python 2 support.
        # useless-object-inheritance:
        #     A Python-3-only feature. Though we should use them wherever
        #     possible once we drop Python 2 support.
        #
        "command": "pylint --disable=bad-continuation,raise-missing-from,consider-using-f-string,super-with-arguments,useless-object-inheritance python/qt_core tests",
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

    env.PYTHONPATH.append(os.path.join(root, "python.egg"))
