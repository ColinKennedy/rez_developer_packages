name = "rez_docbot"

version = "1.0.0"

description = "Auto build, link, and publish documentation, via Rez"

authors = ["ColinKennedy"]

build_command = "python -m rez_build_helper --items bin python"

private_build_requires = ["rez_build_helper-1.8+<2"]

requires = [
    "Sphinx-1.8+<2",
    "six-1.16+<2",
]


def commands():
    import os

    env.PYTHONPATH.append(os.path.join(root, "python"))
