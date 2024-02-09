#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""A collection of exceptions for the ``rez_pip_boy`` CLI."""


class ExceptionBase(Exception):
    """A base to use when creating exception subclasses."""

    code = -1


class MissingDestination(ExceptionBase):
    """Whenever the user gives a folder on-disk which doesn't exist."""

    code = 10


class MissingTarLocation(ExceptionBase):
    """If there's no defined fallback path for downloaded .tar.gz files to go."""

    code = 20


class BadTarLocation(ExceptionBase):
    """If a place to download .tar.gz files was found but it doesn't exist on-disk."""

    code = 30
