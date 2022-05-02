"""A series of functions which extend Rez's diff API.

See Also:
    :meth:`rez.resolved_context.ResolvedContext.get_resolve_diff`.

"""

import collections


def get_request_diff(names, diff):
    """Filter ``diff`` with the Rez package requests, ``names``.

    Args:
        names (set[str]):
            Each Rez package family name to filter by. Only variants /
            packages in ``diff`` which match a name in this parameter will be
            returned.
        diff (dict[str, dict[str, list] or list]):
            The Rez diff (usually generated using
            :meth:`rez.resolved_context.ResolvedContext.get_resolve_diff`)
            to filter by.

    Returns:
        dict[str, dict[str, list] or list]: The filtered diff.

    """
    output = dict()

    for key, data in diff.items():
        if isinstance(data, collections.MutableMapping):
            output[key] = {
                name: packages for name, packages in data.items() if name in names
            }
        else:
            output[key] = [package for package in data if package.name in names]

    return output
