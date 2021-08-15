name = "rez_sphinx"

# TODO : Replace this with a `1` major, later
version = "0.1.0"

description = "Integrate Sphinx, the Python documentation generator, with Rez packages."

authors = ["ColinKennedy (colinvfx@gmail.com)"]

help = [["README", "README.md"]]

private_build_requires = ["python-2", "rez_build_helper-1.1+<2"]

# TODO : Replace this with a `1` major, later
requires = ["rez_plugin-0"]

build_command = "python -m rez_build_helper --items python bin"

tests = {
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
