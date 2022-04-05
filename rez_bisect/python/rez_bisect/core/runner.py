from __future__ import division


def _reduce_to_two_contexts(caller, contexts):
    current = contexts
    upper_bound = len(contexts) // 2
    lower_bound = 0

    while len(current) > 1:
        left = current[lower_bound:upper_bound]
        latest_left = left[-1]

        if caller(latest_left):
            # TODO : Check if this is an off-by-one error (e.g. 0-through-9)
            distance = upper_bound - lower_bound
            old_upper_bound = upper_bound
            lower_bound = upper_bound
            upper_bound = old_upper_bound + distance
        else:
            lower_bound = lower_bound // 2  # Further reduce to the left side

    raise ValueError(current)


def bisect(caller, contexts):
    last_good, first_bad = _reduce_to_two_contexts(caller, contexts)

    raise ValueError(last_good, first_bad)
