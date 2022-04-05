from __future__ import division

import collections

_BisectSummary = collections.namedtuple("_BisectSummary", "last_good, first_bad, diff")


def _get_right_side_bounds(lower_bound, upper_bound):
    # TODO : Check if this is an off-by-one error (e.g. 0-through-9)
    distance = upper_bound - lower_bound
    old_upper_bound = upper_bound
    lower_bound = upper_bound
    upper_bound = old_upper_bound + distance

    return lower_bound, upper_bound


def _reduce_to_two_contexts(caller, contexts):
    current = contexts
    upper_bound = len(contexts) // 2
    lower_bound = 0

    while upper_bound - lower_bound != 1:
        left = current[lower_bound:upper_bound]
        latest_left = left[-1]

        if caller(latest_left):
            lower_bound, upper_bound = _get_right_side_bounds(lower_bound, upper_bound)
        else:
            lower_bound = lower_bound // 2  # Further reduce to the left side

    return lower_bound, upper_bound


def bisect(caller, contexts):
    last_good, first_bad = _reduce_to_two_contexts(caller, contexts)
    diff = contexts[last_good].get_resolve_diff(contexts[first_bad])

    return _BisectSummary(last_good=last_good, first_bad=first_bad, diff=diff)
