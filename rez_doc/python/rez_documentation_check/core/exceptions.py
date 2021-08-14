#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Custom exceptions that make it easier to use the command-line tool."""


class SphinxFileMissing(Exception):
    """Any time an expected, required Sphinx-related file is missing. (usually the conf.py)."""

    pass
