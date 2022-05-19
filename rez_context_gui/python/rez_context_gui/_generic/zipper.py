import itertools


def zip_equal(*iterables):
    # Reference: https://stackoverflow.com/a/69485272/3626104

    # For trivial cases, use pure zip.
    if len(iterables) < 2:
        return zip(*iterables)

    # Tail for the first iterable
    first_stopped = False
    def first_tail():
        nonlocal first_stopped
        first_stopped = True
        return
        yield

    # Tail for the zip
    def zip_tail():
        if not first_stopped:
            raise ValueError(f'zip_equal: first iterable is longer')
        for _ in itertools.chain.from_iterable(rest):
            raise ValueError(f'zip_equal: first iterable is shorter')
            yield

    # Put the pieces together
    iterables = iter(iterables)
    first = itertools.chain(next(iterables), first_tail())
    rest = list(map(iter, iterables))
    return itertools.chain(zip(first, *rest), zip_tail())

