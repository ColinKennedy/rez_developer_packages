#!/usr/bin/env python
# -*- coding: utf-8 -*-

name = "rez_build_helper"

version = "1.3.0"

description = "Build Rez packages using Python"

authors = ["ColinKennedy"]

help = [
    ["README", "README.md"],
]

build_command = 'python {root}/rezbuild.py {install}'

uuid = "168c5114-a951-4834-a744-dae1331e375e"


def commands():
    import os

    env.PYTHONPATH.append(os.path.join("{root}", "python"))
