#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Configurable functions to control the output of functions from this package."""

from rez import serialise
import wurlitzer


REZ_PACKAGE_NAMES = frozenset("package." + extension.lstrip(".") for format_ in serialise.FileFormat for extension in format_.value)


def get_context():
    """:class:`contextlib.GeneratorContextManager`: Silence all C-level stdout messages."""
    return wurlitzer.pipes()
