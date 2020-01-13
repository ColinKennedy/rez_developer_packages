#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os


# Note : Possibly replace this function with :func:`setuptools.findall`?
def iter_python_files(item):
    """Find every Python file from the given file or folder.

    Args:
        item (str):
            The file or folder to search for Python files.
            If `item` is a Python file, just yield itself.

    Yields:
        str: The absolute path to a Python source code file (".py" file).

    """

    def _is_python_file(path):
        """bool: Check if `path` is a Python source file (un-compiled)."""
        return path.endswith(".py")

    if os.path.isfile(item):
        if not _is_python_file(item):
            yield
            return

        yield item

    for root, _, files in os.walk(item):
        for path in files:
            if _is_python_file(path):
                yield os.path.join(root, path)
