# -*- coding: utf-8 -*-

name = "parso_helper"

version = "1.2.0"

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

uuid = "c989f6ef-7f52-4acf-8660-e0268049f700"


def commands():
    import os

    env.PYTHONPATH.append(os.path.join("{root}", "python"))
