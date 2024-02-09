#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""A thin wrapper around :mod:`cli` that automatically builds / symlinks Rez packages."""

from __future__ import print_function

import logging
import sys

from . import cli, exceptions

_LOGGER = logging.getLogger("rez_build_helper")
_HANDLER = logging.StreamHandler(sys.stdout)
_HANDLER.setLevel(logging.WARNING)
_FORMATTER = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
_HANDLER.setFormatter(_FORMATTER)
_LOGGER.addHandler(_HANDLER)
_LOGGER.setLevel(logging.WARNING)

try:
    cli.main(sys.argv[1:])
except exceptions.NonRootItemFound as error:
    print(error, file=sys.stderr)
    print("Please check spelling and try again.")
