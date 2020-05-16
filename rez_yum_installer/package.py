#!/usr/bin/env python
# -*- coding: utf-8 -*-

name = "rez_yum_installer"

version = "1.0.0"

description = "Install yum (Fedora) packages as easily as rez-pip!"

authors = ["ColinKennedy (colinvfx@gmail.com)"]

help = [["README", "README.md"]]

private_build_requires = ["rez_build_helper-1+<2"]

build_command = "python -m rez_build_helper --items python"

requires = [
    "functools32-3.2+<4",
    "python-2+<3",  # TODO : Yum apparently is only for Python 2, at the moment
    "python_rpm_spec-0.7+<1",
    "rez-2.56+<3",
    # "yum",  TODO : Find if there's a way to make sure this exists
]

def commands():
    import os

    env.PYTHONPATH.append(os.path.join("{root}", "python"))
