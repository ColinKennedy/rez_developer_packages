#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""A collection of exceptions for the ``rez_pip_boy`` CLI."""


DUPLICATE_DOUBLE_DASH_EXIT_CODE = 2
MISSING_DESTINATION_FOLDER_EXIT_CODE = 4
MISSING_DOUBLE_DASH_EXIT_CODE = 3


class DuplicateDoubleDash(Exception):
    """If the user adds more than one " -- " separator."""


class MissingDoubleDash(Exception):
    """If the user tries to call `rez_pip_boy` without a " -- " separator."""


class MissingDestination(Exception):
    """Whenever the user gives a folder on-disk which doesn't exist."""


class SwappedArguments(Exception):
    """When the user adds `rez-pip` arguments to the right of the " -- " instead of the left."""
