#!/usr/bin/env python

import json
import os
import shlex

from rez import resolved_context


def to_context(data):
    if os.path.isfile(data):
        return resolved_context.ResolvedContext.load(data)

    try:
        json.loads(data)
    except ValueError:
        # `data` was not a JSON string. Treat it like a Rez request and resolve it
        return resolved_context.ResolvedContext(shlex.split(data))

    # TODO : Add a unittest here
    return resolved_context.ResolvedContext.resolved_context(data)
