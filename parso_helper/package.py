# -*- coding: utf-8 -*-

name = "parso_helper"

version = "1.0.0"

description = "Functions that make using parso a bit easier"

authors = [
    "Colin Kennedy (ColinKennedy)",
]

private_build_requires = ["rez_build_helper-1+<2"]

requires = [
    "parso-0.5+<1",
    "python-2",
]

build_command = "python -m rez_build_helper --items python"


def commands():
    import os

    env.PYTHONPATH.append(os.path.join("{root}", "python"))
