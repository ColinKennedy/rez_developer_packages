"""Any miscellaneous function for making Python path parsing simpler."""

import os


def normalize(path, root):
    """Resolve ``path`` into an absolute path to a file / folder.

    Args:
        path (str):
            An absolute or relative path to make absolute.
        root (str):
            An absolute path which prepends to ``path``, if ``path`` is relative.

    Returns:
        str: The absolute path to a file or folder on-disk for ``path``.

    """
    if os.path.isabs(path):
        return path

    return os.path.normcase(os.path.join(root, path))
