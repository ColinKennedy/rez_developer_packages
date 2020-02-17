# -*- coding: utf-8 -*-

name = "rez_bump"

version = "1.0.0"

description = "Control the version value of Rez packages"

authors = [
    "Colin Kennedy (ColinKennedy)",
]

requires = [
    "python-2+<3",
    "rez-2.42+<3",
    "rez_utilities-1.4+<2",
]


def commands():
    import os

    env.PYTHONPATH.append(os.path.join("{root}", "python"))
