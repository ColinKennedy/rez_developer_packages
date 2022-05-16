name = "rez_context_gui"

version = "1.0.0"

description = "View a Rez context as nodes in a GUI. Like rez-context --graph, but interactive!"

authors = ["ColinKennedy"]

requires = [
    "Qt.py-1.3+<2",
    "python-2.7+<4",
    "rez-2.104+<3",
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


def commands():
    import os

    env.PATH.append(os.path.join(root, "bin"))
    env.PYTHONPATH.append(os.path.join(root, "python.egg"))
    # TODO : Remove this "vendors" folder later
    env.PYTHONPATH.append(os.path.join(root, "vendors"))
