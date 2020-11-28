#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Generic functions that help iterating over containers and other iterables."""


def iter_is_last(container):
    """Iterate over a Python object and check if iterator's at the last element.

    Reference:
        https://stackoverflow.com/a/1630350

    Args:
        container (iter[object]): Some iterable object.

    Raises:
        ValueError: If `container` isn't iterable.

    Yields:
        tuple[bool, object]:
            Return True if iterator's the last index, otherwise False + the
            original object.

    """
    # Get an iterator and pull the first value.
    try:
        iterator = iter(container)
    except TypeError:
        raise ValueError(
            'Container "{container}" is not iterable.'.format(container=container)
        )

    try:
        last = next(iterator)
    except StopIteration:
        # Prevents a DeprecationWarning in Python 3.5+
        # Reference: https://stackoverflow.com/a/53373901
        #
        return
        yield

    # Run the iterator to exhaustion (starting from the second value).
    for value in iterator:
        # Report the *previous* value (more to come).
        yield False, last

        last = value

    # Report the last value.
    yield True, last
