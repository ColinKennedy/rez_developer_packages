#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Configurable functions to control the output of functions from this package."""

import wurlitzer


def get_context():
    """:class:`contextlib.GeneratorContextManager`: Silence all C-level stdout messages."""
    return wurlitzer.pipes()
