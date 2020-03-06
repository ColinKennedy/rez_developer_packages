#!/usr/bin/env python
# -*- coding: utf-8 -*-

name = "rez_build_helper"

version = "1.2.0"

description = "Build Rez packages using Python"

authors = ["ColinKennedy"]

help = [
    ["README", "README.md"],
]

build_command = 'python {root}/rezbuild.py {install}'


def commands():
    import os

    env.PYTHONPATH.append(os.path.join("{root}", "python"))
