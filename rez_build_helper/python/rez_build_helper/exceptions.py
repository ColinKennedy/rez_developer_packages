#!/usr/bin/env python
# -*- coding: utf-8 -*-

""":mod:`rez_build_helper` specific exceptions for CLI use."""


class NonRootItemFound(Exception):
    """Only root file(s)/folder(s) may be converted into .egg files."""
