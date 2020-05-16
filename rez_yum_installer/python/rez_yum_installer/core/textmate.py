#!/usr/bin/env python
# -*- coding: utf-8 -*-

from rez.utils import pip


def convert_to_rez_package_name(name):
    # Not sure if it's okay to be using a pip-specific replacement here. But it does work!
    return pip.pip_to_rez_package_name(name)


def requirements_to_text(requirements):
    return [str(requirement) for requirement in requirements]
