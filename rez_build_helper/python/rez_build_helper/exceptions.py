#!/usr/bin/env python
# -*- coding: utf-8 -*-

""":mod:`rez_build_helper` specific exceptions for CLI use."""


class _BaseException(Exception):
    """A base class for all other exceptions to subclass and use."""


class NonRootItemFound(_BaseException):
    """Only root file(s)/folder(s) may be converted into .egg files."""


class UserInputError(_BaseException):
    """Only root file(s)/folder(s) may be converted into .egg files."""
