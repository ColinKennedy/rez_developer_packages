name = "rez_pip_boy"

version = "1.0.0"

description = "Convert an installed pip package back into a source package"

authors = [
    "Colin Kennedy",
]

help = [["README", "README.md"]]

private_build_requires = ["rez_build_helper-1+<2"]

build_command = "python -m rez_build_helper --items python"

requires = [
    "python-2+<3",
    "rez-2.47+<3",
    "rez_utilities-1.4+<2",
]


def commands():
    import os

    env.PYTHONPATH.append(os.path.join("{root}", "python"))
