#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The main module that gets import module information from Python files.

Unlike other parsers, this module can find conditional, nested, and
highly complex Python imports by parsing Python files using AST,
directly.

"""

import ast
import copy
import logging
import os
import re
import sys

_DOTS_EXPRESSION = re.compile(r"^\s*from\s+(?P<dots>\.+)*.+")
_LOGGER = logging.getLogger(__name__)


# TODO : This really needs to be renamed to "Namespace"
class Module(object):
    """A wrapper class around a Python namespace."""

    def __init__(
        self, base, leaf, row, level=0, alias="", pragma=None
    ):  # pylint: disable=too-many-arguments
        """Create the object and store its namespace information + its caller context.

        Here's an example import with each of its sections split up.

        ::

            from ..some.parts import foo as bar
                 | |        |         |      |
                 | +--------+         |      |
             level    base          leaf   alias

        Args:
            base (str): The first part of an import.
            leaf (str): The last namespace part of an import.
            row (int): The 1-based line number where the module import comes from.
            level (int, optional): `level` specifies how many folders up
                the import is. The default value means "no folder level
                context". Each prefix "." added is an extra +1 level.
                Default: 0.
            alias (str, optional): The user-provided alternative name for `leaf`.
                Default: "".
            pragma (object, optional): An extra context for the called import statement.
                If nothing is given, it just means "process the import
                as-normal". Default is None.

        """
        super(Module, self).__init__()

        self._base = base
        self._leaf = leaf
        self._row = row
        self._level = level
        self._alias = alias
        self._pragma = pragma

    @classmethod
    def from_context(cls, module, pragma=None):
        """Create a new instance, using `module` as a base.

        If the user has a special context that they'd like to provide. they can add it
        as an attribute override.

        Args:
            module (:class:`Module`):
                The import to copy from.
            pragma (NoneType, optional): The context to override. Otherwise,
                :meth:`Module.get_pragma` will be used instead. Default
                is None.

        """
        return cls(
            module.get_base(),
            module.get_leaf(),
            module.get_row(),
            level=module.get_level(),
            alias=module.get_alias(),
            pragma=pragma or module.get_pragma(),
        )

    def get_alias(self):
        """str: An optional name to use for the module."""
        return self._alias

    def get_base(self):
        """str: Every part of the import leading up to the last part of namespace."""
        return self._base

    def get_leaf(self):
        """str: The last namespace part of the import."""
        return self._leaf

    def get_level(self):
        """int: The number of folders up from the current Python module to search for an import."""
        return self._level

    def get_pragma(self):
        """object: The context of the import."""
        return self._pragma

    def get_row(self):
        """int: The 1-based line where the import statement is located in the Python source code."""
        return self._row

    def get_namespace(self):
        """str: The un-modified (alias-less) dotted Python namespace."""
        if self._leaf == "*" or not self._leaf:
            return self._base

        return self._base + "." + self._leaf

    def iter_parent_namespaces(self):
        """Get the dot-separated namespaces above the current namespace.

        For example, if this namespace is "foo.bar.bazz", this method yields
        "foo.bar" and then "foo", in that order.

        Yields:
            str: Any namespace above the current instance.

        """
        namespace = self.get_namespace()
        parts = namespace.split(".")

        while parts:
            joined = ".".join(parts[:-1])

            if not joined:
                break

            yield joined

            parts = joined.split(".")

    def set_from_namespace(self, namespace):
        """Change this module's import statement.

        Warning:
            Most modules should be initialized with correct import /
            namespace data. This method should only be used for edge
            cases like patching issues that couldn't be caught when the
            instance was first created.

        Args:
            namespace (str): A dotted Python namespace. e.g. "foo.bar.bazz".

        """
        parts = namespace.split(".")

        if len(parts) == 1:
            base = parts[0]
            leaf = ""
        else:
            base = ".".join(parts[:-1])
            leaf = parts[-1]

        self._base = base
        self._leaf = leaf

    def __repr__(self):
        """str: Get an exact replication of this instance."""
        return (
            "{self.__class__.__name__}("
            "{self._base!r}, "
            "{self._leaf!r}, "
            "{self._row}, "
            "level={self._level}, "
            "alias={self._alias!r}, "
            "pragma={self._pragma}"
            ")".format(self=self)
        )


class ImportVisitor(ast.NodeVisitor):
    """Find every import statement in some Python code."""

    def __init__(self, code):
        """Store the Python source code that this instance will walk over for imports.

        Args:
            code (str): The Python source code that will later be tokenized.

        """
        super(ImportVisitor, self).__init__()

        self.modules = []
        self._lines = code.split("\n")

    def _patch_from_import(self, node):
        """Add relative import dots to a module, if needed.

        This function works because Python import lines are not
        functions, they're statements. So they must be the first
        non-whitespace character on a given line. We also know what
        line the import starts on, which makes it very easy to get the
        relative "."s that we need.

        Args:
            node (:class:`ast.Node`):
                An ast node that may or may not be a relative import.
                For some reason, ast nodes that are relative imports do
                NOT show the prefix "."s. But we need these, so we'll
                detect and return them.

        Returns:
            str:
                The beginning namespace of a Python import, including
                its "." prefix. e.g. "..foo.bar" instead of "foo.bar".

        """
        source = self._lines[node.lineno - 1]
        match = _DOTS_EXPRESSION.match(source)

        if match and match.group("dots"):
            return match.group("dots") + node.module.lstrip(".")

        return (
            node.module or ""
        )  # `module` is None when the import is `from . import foo`

    def visit_Import(self, node):  # pylint: disable=invalid-name
        """Add import statement(s) to the most recent imports.

        Args:
            node (:class:`ast.Import`):
                The import statement to parse into a :class:`Module` object.

        """
        self.modules.extend(
            Module(
                alias.name, "", node.lineno, level=0, alias=alias.asname or alias.name
            )
            for alias in node.names
        )

        self.generic_visit(node)

    def visit_ImportFrom(self, node):  # pylint: disable=invalid-name
        """Add `from X import Y` statement(s) to the most recent imports.

        Args:
            node (:class:`ast.ImportFrom`):
                The import statement to parse into a :class:`Module` object.

        """
        base = (
            node.module or ""
        )  # `module` is None when the import is `from . import foo`

        if base == "__future__":
            self.generic_visit(node)

            return  # Ignore these.

        if base:
            base = self._patch_from_import(node)

        for alias in node.names:
            name = alias.name
            as_ = alias.asname

            if name == "*":
                # We aren't going to track what the module is importing
                module = Module(base, "*", node.lineno, level=node.level, alias=None)
            else:
                module = Module(
                    base, name, node.lineno, level=node.level, alias=as_ or name
                )

            self.modules.append(module)

        self.generic_visit(node)


def _is_relative_namespace(namespace):
    """Check if a Python namespace is a relative namespace.

    Args:
        namespace (str): A dotted Python string, such as "foo.bar" or ".foo.bar".

    Returns:
        bool: If the namespace is relative (starts with a ".").

    """
    return namespace.startswith(".")


def _find_first_pythonpath_root_namespace(path):
    """Find the first Python namespace that contains `path` as a sub-directory.

    Args:
        path (str):
            The absolute path to a Python file or folder. This path is
            assumed importable somewhere in the user's PYTHONPATH.

    Raises:
        RuntimeError: If `path` is nowhere in the user's PYTHONPATH environment.

    Returns:
        str: The found, dotted Python namespace "foo.bar.thing".

    """

    def _get_relative_path(path, directory):
        """Find the relative path of a directory and another directory or file path.

        This function takes symlinks into account and should work
        regardless of how the user has their paths set up.

        Reference:
            https://stackoverflow.com/q/3812849/3626104

        Args:
            path (str):
                The file or folder that may be a sub-file / sub-folder of `directory`.
            directory (str):
                The absolute path to a folder that may be a root folder of `path`.

        Returns:
            str: If `path` is inside of `directory`, it will return a non-empty string.
                 Otherwise, return an empty string.

        """
        directory = os.path.join(os.path.realpath(directory), "")
        path = os.path.realpath(path)

        # return true, if the common prefix of both is equal to directory
        # e.g. /a/b/c/d.rst and directory is /a/b, the common prefix is /a/b
        #
        if os.path.commonprefix([path, directory]) == directory:
            return os.path.normcase(os.path.relpath(path, directory))

        return ""

    for item in sys.path[:]:
        if not item:
            # Prevent a ValueError and skip it.
            _LOGGER.warning("Empty path in sys.path was found. Skipping.")

            continue

        relative = _get_relative_path(path, item)

        if not relative:
            continue

        return relative.replace(os.sep, ".")

    raise RuntimeError('No root path could be found to "{path}".'.format(path=path))


def _make_absolute(namespace, path):
    """Convert a Python namespace into an absolute namespace.

    Args:
        namespace (str):
            The relative Python path to make into an absolute path. If
            the path is already absolute, it is returned, unmodified.
        path (str):
            The absolute path to a Python file or folder. This path is
            assumed importable somewhere in the user's PYTHONPATH.

    Returns:
        str: The found absolute path.

    """
    if not namespace.startswith("."):
        return namespace

    beginning = namespace[: len(namespace) - len(namespace.lstrip("."))]
    parents = len(beginning)

    for _ in range(parents):
        path = os.path.dirname(path)

    root_namespace = _find_first_pythonpath_root_namespace(path)

    return root_namespace + "." + namespace.lstrip(".")


def _resolve_to_absolute(modules, path):
    """Change the given module imports into absolute imports.

    Args:
        modules (iter[:class:`.Module`]):
            Absolute or relative imports.
        path (str):
            The absolute path to a Python file or folder. This path is
            assumed importable somewhere in the user's PYTHONPATH.

    Returns:
        list[:class:`.Module`]: The found Python imports.

    """
    output = []

    for module in modules:
        namespace = module.get_namespace()

        if not _is_relative_namespace(namespace):
            output.append(module)

            continue

        absolute_namespace = _make_absolute(namespace, path)
        module = copy.deepcopy(module)
        module.set_from_namespace(absolute_namespace)
        output.append(module)

    return output


def get_namespaces_from_file(path, absolute=True):
    """Get every Python import in the given Python file.

    Args:
        path (str):
            A Python file that may or may not have Python imports in it.
            Every import found will be returned.
        absolute (bool, optional):
            If True, the found imports will be forced into absolute
            imports. If False, any relative imports will stay relative.
            Default is True.

    Returns:
        list[:class:`.Module`]: The found Python imports.

    """
    modules = parse_python_source_file(path)

    if absolute:
        modules = _resolve_to_absolute(modules, path)

    return modules


def parse_python_source_file(path):
    """Get all of the import statements from some Python file.

    Args:
        path (str): The absolute file path to a Python file.

    Returns:
        list[:class:`Module`]: Dequeue any remaining modules and return them.

    """
    contents = open(path, "rU").read()

    return parse_python_source_code(contents)


def parse_python_source_code(code):
    """Get all of the import statements from some Python code.

    Args:
        code (str): Python source code to get import statemnts from.

    Returns:
        list[:class:`Module`]: Dequeue any remaining modules and return them.

    """
    parser = ast.parse(code)
    visitor = ImportVisitor(code)
    visitor.visit(parser)

    return set(visitor.modules)
