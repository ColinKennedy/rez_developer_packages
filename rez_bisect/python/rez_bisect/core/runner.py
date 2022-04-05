from __future__ import division

import collections

_BisectSummary = collections.namedtuple("_BisectSummary", "last_good, first_bad, diff")


def _get_right_side_bounds(lower_bound, upper_bound):
    # TODO : Check if this is an off-by-one error (e.g. 0-through-9)
    # tests.test_run.CasePositioning.test_permutations test `4` seems to show
    # that it is off by 1!  We end up re-using the same index multiple times
    # for the lower / upper bound. Fix!
    #
    distance = upper_bound - lower_bound
    old_upper_bound = upper_bound
    lower_bound = upper_bound
    upper_bound = old_upper_bound + distance

    return lower_bound + 1, upper_bound


def _reduce_to_two_contexts(has_issue, contexts):
    current = contexts
    upper_bound = len(contexts) // 2
    lower_bound = 0

    while True:
        print('lower / upper', lower_bound, upper_bound)

        if upper_bound == lower_bound + 1:
            # We've reached the end game. One of these 2 contexts has to be the
            # problem. Now we just need to find out which.
            #
            if has_issue(current[lower_bound]):
                return lower_bound - 1, lower_bound

            return lower_bound, upper_bound

        left = current[lower_bound:upper_bound]
        latest_left = left[-1]

        if not has_issue(latest_left):
            # Select the right side
            lower_bound, upper_bound = _get_right_side_bounds(lower_bound, upper_bound)
        else:
            # Further reduce to the left side
            upper_bound = upper_bound - ((upper_bound - lower_bound) // 2)


def bisect(has_issue, contexts):
    count = len(contexts)
    if count > 2:
        last_good, first_bad = _reduce_to_two_contexts(has_issue, contexts)
    elif count == 2:
        last_good = 0
        first_bad = 1
    elif count == 1:
        raise NotImplementedError()  # TODO : Write here
    elif not count:
        raise NotImplementedError()  # TODO : Write here

    diff = contexts[last_good].get_resolve_diff(contexts[first_bad])

    return _BisectSummary(last_good=last_good, first_bad=first_bad, diff=diff)
