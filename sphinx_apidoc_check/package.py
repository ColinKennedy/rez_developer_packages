# -*- coding: utf-8 -*-

name = "sphinx_apidoc_check"

version = "1.0.0"

description = (
    "Check if the user needs to re-run ``sphinx-apidoc`` on their Python package"
)

authors = [
    "ColinKennedy (colinvfx@gmail.com)",
]

requires = [
    "Sphinx-1+<2",
    "python-2+",
    "python_compatibility-1+<2",
]

private_build_requires = [
    "rez_build_helper-1+<2",
]

build_command = "python -m rez_build_helper --items bin python"

tests = {
    "unittest": "python -m unittest discover",
}


def commands():
    import os

    env.PATH.append(os.path.join("{root}", "bin"))
    env.PYTHONPATH.append(os.path.join("{root}", "python"))
