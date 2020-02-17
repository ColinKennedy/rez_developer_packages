#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""All exceptions used to make the user's CLI experience as smooth as possible."""


class InvalidDirectory(Exception):
    """If the user provides a directory for a Rez package but no Rez package exists."""

    error_code = 6


class InvalidInput(Exception):
    """A variant of `ValueError`, but for the CLI.

    When the user provides bad input, to avoid spitting a huge traceback
    and just give them concise details, this class was made. This is
    done so if a bug occurs and some function (that the user didn't have
    control over) raises ValueError, then that traceback will still get
    printed to the user.

    """

    error_code = 4


class MissingDirectory(Exception):
    """If the user provides a non-existent directory for a Rez package."""

    error_code = 5


class MissingNamespaces(Exception):
    """An exception to raise if the user doesn't link a Python namespace to a Rez package.

    If the user provides a namespace to find or a namespace to replace
    but doesn't pair it with a Rez package, even if an import is found
    and replaced, `rez_move_imports` won't know how to modify the user's
    Rez package dependencies in response to that change.

    So every namespace must be linked with a Rez package for this CLI to work.

    """

    error_code = 3
