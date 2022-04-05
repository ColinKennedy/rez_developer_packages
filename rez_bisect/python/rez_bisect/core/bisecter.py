from __future__ import division


def bisect_right(caller, sequence, low=0, high=None):
    # """Return the index where to insert item x in list a, assuming a is sorted.
    #
    # The return value i is such that all e in a[:i] have e <= x, and all e in
    # a[i:] have e > x.  So if x already appears in the list, a.insert(x) will
    # insert just after the rightmost x already there.
    #
    # Optional args low (default 0) and high (default len(a)) bound the
    # slice of a to be searched.
    # """
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
