#!/usr/bin/env python
# -*- coding: utf-8 -*-


class CoreException(Exception):
    pass


class DirectoryDoesNotExist(CoreException):
    pass


class InvalidSphinxArguments(CoreException):
    pass


class NoDryRun(CoreException):
    pass
