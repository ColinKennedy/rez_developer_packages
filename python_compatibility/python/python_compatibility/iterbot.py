#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Generic functions that help iterating over containers and other iterables."""


def iter_is_last(container):
    """Iterate over a Python object and check if it's at the last element.

    Args:
        container (iter[object]): Some iterable object.

    Raises:
        ValueError: If `container` isn't iterable.

    Yields:
        tuple[bool, object]:
            Return True if it's the last index, otherwise False + the
            original object.

    """
    try:
        iterator = iter(container)
    except TypeError:
        raise ValueError('Container "{container}" is not iterable.'.format(container=container))

    next_value = None
    did_iterate = False

    while True:
        try:
            value = next(iterator)
        except StopIteration:
            break

        did_iterate = True

        yield False, value

        try:
            next_value = next(iterator)
        except StopIteration:
            break

    if did_iterate:
        yield True, next_value
