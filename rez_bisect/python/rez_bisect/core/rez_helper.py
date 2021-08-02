#!/usr/bin/env python

"""Generic functions to make working with Rez a bit easier."""

import collections
import json
import os
import shlex

from rez import resolved_context


def to_context(data):
    """Convert some user-input into a Rez context.

    Args:
        data (str or dict):
            Either a file path on disk to a Rez context, or a JSON
            string, or a Python dict which represents a Rez context or a
            regular string which represents a resolve request, which a
            context will be generated for.

    Returns:
        :class:`rez.resolved_context.ResolvedContext`: The generated context.

    """
    if os.path.isfile(data):
        return resolved_context.ResolvedContext.load(data)

    if isinstance(data, collections.MutableMapping):
        return resolved_context.ResolvedContext.resolved_context(json.dumps(data))

    try:
        json.loads(data)
    except ValueError:
        # `data` was not a JSON string. Treat it like a Rez request and resolve it
        return resolved_context.ResolvedContext(shlex.split(data))

    # TODO : Add a unittest here
    return resolved_context.ResolvedContext.resolved_context(data)
