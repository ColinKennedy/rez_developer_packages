#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""A thin wrapper around :mod:`cli` that automatically builds / symlinks Rez packages."""

from __future__ import print_function

import sys

from . import cli, exceptions

try:
    cli.main(sys.argv[1:])
except exceptions.NonRootItemFound as error:
    print(error, file=sys.stderr)
    print("Please check spelling and try again.")
