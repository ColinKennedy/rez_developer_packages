#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Any function that is needed by "registry.py" and used to find Rez package URLs."""


def get_default_urls():
    """Get the expected URLs for finding Rez package documentation.

    Each URL is formatted by a :class:`rez.packages_.Package` instance
    to create a complete URL.

    Returns:
        list[str]: The (Python) documentation URL templates.

    """
    return [
        "http://{package.name}.readthedocs.io/en/v{package.version}",
        "http://{package.name}.readthedocs.io/en/latest",
        "http://{package.name}.readthedocs.io",
    ]
