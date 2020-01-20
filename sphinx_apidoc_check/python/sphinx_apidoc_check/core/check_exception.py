#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The exceptions used by this API."""


class CoreException(Exception):
    """A base exception that all of the exceptions in ``sphinx_apidoc_check`` subclass."""

    pass


class DirectoryDoesNotExist(CoreException):
    """If the user specifies a directory with the "--directory" flag that doesn't exist."""

    pass


class InvalidSphinxArguments(CoreException):
    """If the user calls ``sphinx-apidoc`` with missing, required arguments."""

    pass


class NoDryRun(CoreException):
    """The user must include --dry-run in their shell command to ``sphinx-apidoc``."""

    pass
