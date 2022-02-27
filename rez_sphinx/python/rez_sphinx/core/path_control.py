"""Miscellaneous functions which make working with file paths easier."""

import os


def expand_path(path):
    """Convert ``path`` from a relative, possibly symlinked location to a real path.

    Note:
        ``path`` does not need to exist as a file on-disk.

    Args:
        path (str):
            It could be ".", indicating the current directory. Or "../" meaning
            the parent directory, or an already absolute path.

    Returns:
        str: The expanded path.

    """
    return os.path.normpath(os.path.realpath(path))
