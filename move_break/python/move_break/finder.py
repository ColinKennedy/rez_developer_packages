#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""A module for finding Python files name import namespaces.

These functions tend to be used by other packages, which is why they're included
as part of this package's API.

"""

import copy
import os

import parso

from .core import parser
from .core.parsers import base


_ALLOWED_ERROR_CODES = (
    903,  # IndentationError << This package can handle indentation issues, no problem
)

def expand_paths(path, fallback=""):
    """Find every Python file in `path`.

    Args:
        path (str):
            An absolute or relative path to a Python file or folder on-disk.
        fallback (str, optional):
            A directory on-disk used to resolve `path`, if `path` is
            relative. This path must exist. Default: "".

    Raises:
        ValueError:
            If `path` is not a valid file or folder on-disk or if
            `fallback` is not provided but `path` is relative.

    Returns:
        set[str]: The found Python files.

    """
    if not os.path.isabs(path):
        if not fallback:
            raise ValueError(
                'Path "{path}" cannot be relative if no fallback is given.'.format(
                    path=path
                )
            )

        if not os.path.isdir(fallback):
            raise ValueError(
                'Text "{fallback}" is not a directory.'.format(fallback=fallback)
            )

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
    """Get every Python dot-separated import from some Python file.

    Args:
        path (str): Some Python file on-disk to parse and get imports from.

    Returns:
        set[str]: The found imports. e.g. {"os.path", "foo.bar", "some_custom_module"}.

    """
    graph = get_graph(path)
    imports = parser.get_imports(graph, partial=True)

    return {
        namespace for adapter in imports for namespace in base.get_namespaces(adapter)
    }


def get_graph(path):
    """Convert a file path into a parso graph.

    Args:
        path (str): An absolute path to a file on-disk to load.

    Raises:
        RuntimeError: If `path` has some errors which prevent it from being loaded.

    Returns:
        :class:`parso.python.tree.Module`: The parsed `code`, as a parso object.

    """
    def _get_errors(code):
        grammar = parso.load_grammar()
        module = grammar.parse(code)

        errors = list(grammar.iter_errors(module))

        for error in copy.copy(errors):
            if error.code in _ALLOWED_ERROR_CODES:
                errors.remove(error)

        return errors

    with open(path, "r") as handler:
        code = handler.read()

    errors = _get_errors(code)

    if errors:
        raise RuntimeError(
            'Path "{path}" cannot be loaded as a graph. It has syntax errors.'.format(path=path)
        )

    return parso.parse(code)
