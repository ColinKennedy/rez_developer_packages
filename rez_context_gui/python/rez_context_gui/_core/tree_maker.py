def _make_request_sub_branch(digraph, families):
    for node in digraph:
        if node.get_family_name() not in families:
            node.hide()


def make_conflict_branch(context, digraph=None):
    digraph = digraph or context.graph()
    raise ValueError(context.conflicted_packages())


def make_request_branch(context, digraph=None):
    digraph = digraph or context.graph()
    default_visible_families = {request.name for request in context.requested_packages()}

    everything = _make_request_sub_branch(context, default_visible_families)

    for family in default_visible_families:
        child = _make_request_sub_branch(context, {family})
        everything.addItem(child)

    return everything
