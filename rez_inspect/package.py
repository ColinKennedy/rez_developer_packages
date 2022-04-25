name = "rez_inspect"

version = "1.0.0"

description = "A Rez extension for querying Rez package details, from the terminal."

authors = ["ColinKennedy"]

uuid = "638c332b-92e2-4289-8162-c0a69f39faa7"

private_build_requires = ["rez_build_helper-1+<2"]

build_command = "python -m rez_build_helper --items bin python"


def commands():
    import os

    env.PYTHONPATH.append(os.path.join(root, "python"))
