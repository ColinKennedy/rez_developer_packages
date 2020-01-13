#!/usr/bin/env python
# -*- coding: utf-8 -*-

name = "rez_build_helper"

version = "1.1.0"

description = "Build Rez packages using Python"

authors = ["ColinKennedy"]

build_command = 'python {root}/rezbuild.py {install}'


def commands():
    import os

    env.PYTHONPATH.append(os.path.join("{root}", "python"))
