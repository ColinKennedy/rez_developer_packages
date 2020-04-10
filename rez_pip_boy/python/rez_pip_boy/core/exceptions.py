#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""A collection of exceptions for the ``rez_pip_boy`` CLI."""


class MissingDestination(Exception):
    """Whenever the user gives a folder on-disk which doesn't exist."""

    pass
