#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os

import parso

from .core import parser
from .core.parsers import base


def expand_paths(path, fallback=""):
    # """Find every Python file in `path`.
    #
    # Args:
    #     path (str): An absolute or relative path to a Python file or folder on-disk.
    #
    # Raises:
    #     ValueError: If `path` is not a valid file or folder on-disk.
    #
    # Returns:
    #     set[str]: The found Python files.
    #
    # """
    if not os.path.isabs(path):
        if not fallback:
            raise ValueError('Path "{path}" cannot be relative if no fallback is given.'.format(path=path))

        if not os.path.isdir(fallback):
            raise ValueError('Text "{fallback}" is not a directory.'.format(fallback=fallback))

        path = os.path.normpath(os.path.join(fallback, path))

    if not os.path.exists(path):
        raise ValueError('Path "{path}" is not a file or folder.'.format(path=path))

    if os.path.isfile(path):
        return {path}

    output = set()

    for root, _, files in os.walk(path):
        for path_ in files:
            if path_.endswith(".py"):
                output.add(os.path.join(root, path_))

    return output


def get_namespaces(path):
    graph = get_graph(path)
    imports = parser.get_imports(graph, partial=True)

    return {
        namespace
        for adapter in imports
        for namespace in base.get_namespaces(adapter)
    }


def get_graph(path):
    """:class:`parso.python.tree.Module`: Convert a file path into a parso graph."""
    with open(path, "r") as handler:
        code = handler.read()

    return parso.parse(code)
