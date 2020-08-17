# -*- coding: utf-8 -*-

name = "rez_test_env"

version = "1.0.0"

description = "A small CLI to make `rez-env`-ing test environments in Rez easier."

authors = ["ColinKennedy"]

build_command = "python -m rez_build_helper --items python"


def commands():
    import os

    env.PYTHONPATH.append(os.path.join("{root}", "python"))
