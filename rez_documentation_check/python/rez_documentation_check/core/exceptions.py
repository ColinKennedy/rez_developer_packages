#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Custom exceptions that make it easier to use the command-line tool."""


class BuildPackageDetected(Exception):
    """``rez-documentation-check`` can only be run from a source Rez package.

    It cannot be run on an installed/built/released package.

    """

    pass


class SphinxFileMissing(Exception):
    """Any time an expected, required Sphinx-related file is missing. (usually the conf.py)."""

    pass
