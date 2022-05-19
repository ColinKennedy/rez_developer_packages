name = "rez_context_gui"

version = "1.0.0"

description = "View a Rez context as nodes in a GUI. Like rez-context --graph, but interactive!"

authors = ["ColinKennedy"]

requires = [
    "Qt.py-1.3+<2",
    "python-2.7+<4",
    "qt_core-1+<2",
    "rez-2.104+<3",
    "rez_python_compatibility-2.8+<3",
    "schema-0.7+<1",
    "six-1.16+<2",

    # TODO : Remove these dependencies later. They're required by qtnodes but
    # not by rez_context_gui.
    #
    # See Also: python/rez_context_gui/vendors/qtnodes/requiresments.txt
    #
    "PySide2-5.15+<6",
    "appdirs==1.4.0",
    "pydot-1+<2",
]

private_build_requires = ["rez_build_helper-1.8+<2"]

# TODO : Remove this "vendors" folder later
build_command = "python -m rez_build_helper --items bin vendors --egg python"

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
        "command": "pylint --disable=bad-continuation,raise-missing-from,consider-using-f-string,super-with-arguments,useless-object-inheritance python/rez_context_gui tests",
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

    env.PATH.append(os.path.join(root, "bin"))
    env.PYTHONPATH.append(os.path.join(root, "python.egg"))
    # TODO : Remove this "vendors" folder later
    env.PYTHONPATH.append(os.path.join(root, "vendors"))
