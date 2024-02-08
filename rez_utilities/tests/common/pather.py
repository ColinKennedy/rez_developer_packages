"""Make it easier to deal with OS (Windows) paths."""

import os


def normalize(path):
    r"""Convert ``path`` to its most "real" representation.

    Args:
        path (str):
            The absolute path to change. This path may or may not live on-disk.
            e.g. ``"C:\Users\User~1\path"``.

    Returns:
        str: The converted path. e.g. ``"C:\Users\Username\path"``.

    """
    return os.path.normcase(os.path.realpath(path))
