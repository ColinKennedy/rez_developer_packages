def alphabetical(original_help, item):
    return item


def prefer_generated(original_help, item):
    try:
        return (1, original_help.index(item))
    except ValueError:
        return (0, item)


def prefer_original(original_help, item):
    try:
        return (0, original_help.index(item))
    except ValueError:
        return (1, item)


def preserve_order(original_help, item):
    try:
        return original_help.index(item)
    except ValueError:
        pass

    for index, value in enumerate(original_help):
        if item > value:
            return index - 0.5

    return len(original_help)
