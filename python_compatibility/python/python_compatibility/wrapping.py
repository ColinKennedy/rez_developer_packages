#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Generic-but-still-useful wrappers."""


def run_once(function):
    """Make sure that the given function only ever runs once.

    Reference:
        https://stackoverflow.com/a/4104188/3626104

    Args:
        function (callable): The function that you only ever want to be able to call once.

    Returns:
        callable: The same `function`, but now with logic better controlled.

    """
    def wrapper(*args, **kwargs):
        if not wrapper.has_run:
            wrapper.has_run = True

            return function(*args, **kwargs)

    wrapper.has_run = False

    return wrapper
