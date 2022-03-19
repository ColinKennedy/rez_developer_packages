def is_iterable(value):
    try:
        iter(value)
    except TypeError:
        return False

    return True
