#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Sphinx-related exceptions."""


class SphinxFileBroken(Exception):
    """Any time an expected, required Sphinx-related file exists but is missing data."""
