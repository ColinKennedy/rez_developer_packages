"""A shameless copy of Python's own :mod:`bisect` module.

There's a couple tweaks to make it more useful. But otherwise, it's the same code.

"""

from __future__ import division


# TODO : Double-check if we actually need bisect_left, not bisect_right

def bisect_right(caller, sequence, low=0, high=None):
    """Return the index where `caller`` first occurs in ``sequence``.

    This function assumes that ``sequence`` is sorted.

    The return value index is such that all elements in sequence[:index] return
    ``caller`` value of False and all elements in sequence[index:] return
    ``caller`` value of True.  So if ``caller`` is already True in the list,
    sequence.insert(index, foo) will insert just after the rightmost ``caller``
    where it returns True.

    Args:
        caller (callable[rez.resolved_context.Context] -> bool):
            A function that, if returns False, bisects to the right.  If it
            returns False, we bisect to the left. The returned index is the
            first location in ``sequence`` where ``caller`` returns True.
        sequence (container[rez.resolved_context.Context]):
            Each Rez :ref:`context` to query.
        low (int, optional):
            A 0-based start value to search within. If not provided, the 0th
            index is used.
        high (int, optional):
            A 0-based start value to search within. If not provided, every
            index to the end of ``sequence`` is considered.

    Raises:
        ValueError: If ``low`` is not a positive value.

    Returns:
        int: The found index where ``caller`` first returns True.

    """
    if low < 0:
        raise ValueError("low must be non-negative.")

    if high is None:
        high = len(sequence)

    while low < high:
        middle = (low + high) // 2

        if caller(sequence[middle]):
            high = middle
        else:
            low = middle + 1

    return low
