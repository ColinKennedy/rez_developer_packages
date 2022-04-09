import collections


def filter_by_packages(packages, diff):
    output = {}

    for key, data in diff.items():
        if isinstance(data, collections.MutableMapping):
            new_data = {}

            for name in data.keys():
                if name in packages:
                    new_data[name] = packages[name]

            if new_data:
                output[key] = new_data
        else:
            new_data = []

            for name in data:
                if name in packages:
                    new_data.append(packages[name])

            if new_data:
                output[key] = new_data

    return output


def get_request_diff(names, diff):
    # """Filter ``diff`` with the Rez package requests, ``names``.
    #
    # Args:
    #     names (set[str]):
    #         Each Rez package family name to filter by. Only variants /
    #         packages in ``diff`` which match a name in this parameter will be
    #         returned.
    #     diff (dict[str, dict[str, list] or list]):
    #         The Rez diff (usually generated using
    #         :meth:`rez.resolved_context.ResolvedContext.get_resolve_diff`)
    #         to filter by.
    #
    # Returns:
    #     dict[str, dict[str, list] or list]: The filtered diff.
    #
    # """
    output = dict()

    for key, data in diff.items():
        if isinstance(data, collections.MutableMapping):
            output[key] = {name: packages for name, packages in data.items() if name in names}
        else:
            output[key] = [package for package in data if package.name in names]

    return output
