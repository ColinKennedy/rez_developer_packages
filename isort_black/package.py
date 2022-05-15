name = "isort_black"

version = "1.0.0"

description = 'A simple isort configuration that "plays nice" with black'

help = [["README", "README.md"]]

authors = ["ColinKennedy"]

private_build_requires = ["rez_build_helper-1.8+<2"]

build_command = "python -m rez_build_helper --items .isort.cfg bin"

requires = ["isort-3+<6"]


def commands():
    import os

    env.PATH.append(os.path.join(root, "bin"))
