#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Generic functions that help iterating over containers and other iterables."""

from six import moves


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
        yield  # pylint: disable=unreachable

    # Run the iterator to exhaustion (starting from the second value).
    for value in iterator:
        # Report the *previous* value (more to come).
        yield False, last

        last = value

    # Report the last value.
    yield True, last


def iter_sub_finder(smaller, larger):
    """Find each index of `larger` which contains `smaller`.

    Reference:
        https://stackoverflow.com/a/60819519

    Args:
        smaller (container[object]): Something to search for. e.g. [4, 6].
        larger (container[object]): A bigger container to search with. e.g. [1, 4, 6, -4, 4, 6].

    Raises:
        ValueError: If `smaller` is empty.

    Yields:
        int: Every found index, if any.

    """
    larger_length = len(larger)
    smaller_length = len(smaller)
    stop = larger_length - smaller_length + 1

    if larger_length > 0:
        item = smaller[0]
        index = 0

        try:
            while index < stop:
                index = larger.index(item, index)

                if larger[index:index + smaller_length] == smaller:
                    yield index

                index += 1
        except ValueError:
            return


def make_chains(sequence, size=2):
    """Get each sequential, overlapping chain, from a sequence.

    Example:
        >>> make_chains([0, 1, 2])
        # [(0, 1), (1, 2)]

    Args:
        sequence (container[object]):
            Any container of objects, as long as it supports `len()`.
        size (int, optional):
            The spacing for the chain. You can make "wider" chains but
            setting a higher size value. Default: 2.

    Raises:
        ValueError: If `sequence` cannot be chained or if `size` is not greater than 1.

    Returns:
        list[object]: The generated chain.

    """
    if size < 1:
        raise ValueError('Size "{size}" cannot be less than 1.'.format(size=size))

    try:
        length = len(sequence)
    except TypeError:
        raise ValueError('Item "{sequence}" has no length.'.format(sequence=sequence))

    return [sequence[start : start + size] for start in range(length - size + 1)]


def make_pairs(sequence):
    """Get unique pairs from `sequence`.

    This function differs from :func:`make_chains` in 2 ways

    1. :func:`make_chains` has duplicate values. This function does not
    2. This function will always return pairs.
        - Odd-length containers will have its last index dropped.

    Args:
        sequence (iter[object]): Some object to generate pairs from.

    Raises:
        ValueError: If `sequence` isn't able to be paired.

    Returns:
        list[object]: The created pairs.

    """
    try:
        iterable = iter(sequence)
    except TypeError:
        raise ValueError('Item "{sequence}" is not iterable.'.format(sequence=sequence))

    return moves.zip(iterable, iterable)
