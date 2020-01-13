#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Python project objects."""

import os
import tempfile


def make_fake_python_project():
    """Create a Python package with a nested directory.

    This function is for testing purposes.

    Returns:
        tuple[str, str]: The root folder for the Python package and a nested module.

    """
    directory = tempfile.mkdtemp()
    end = os.path.join(directory, "fake_package", "inner_package", "my_module.py")

    paths = [
        os.path.join(directory, "fake_package", "__init__.py"),
        os.path.join(directory, "fake_package", "inner_package", "__init__.py"),
        end,
    ]

    for path in paths:
        parent = os.path.dirname(path)

        if not os.path.isdir(parent):
            os.makedirs(parent)

        open(path, "a").close()

    return directory, end
