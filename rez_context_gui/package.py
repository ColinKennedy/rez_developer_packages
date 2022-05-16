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
]

private_build_requires = ["rez_build_helper-1.8+<2"]

build_command = "python -m rez_build_helper --items bin --egg python"


def commands():
    import os

    env.PATH.append(os.path.join(root, "bin"))
    env.PYTHONPATH.append(os.path.join(root, "python.egg"))
