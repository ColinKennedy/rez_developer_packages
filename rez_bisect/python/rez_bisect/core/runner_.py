
def _split(good, bad):
    raise ValueError(good.get_resolve_diff(bad))
    # raise ValueError("foo" in bad)
    # for variant in good.resolved_packages:
    #     variant.name


def run(bad, command, good=None):
    if not good:
        # TODO : Add test for this
        raise NotImplementedError("Need to write this")

    added, removed, changed = _split(good, bad)
