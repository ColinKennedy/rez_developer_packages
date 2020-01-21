#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""A module that keeps track of the contexts and checkers to run over a Rez package.

The classes that this module returns will greatly determine whether a
Rez package finds issues our not. You can also add more issue checkers
to enforce better standards for Rez packages, too.

"""

import inspect

from ..plugins.checkers import base_checker
from ..plugins.contexts import base_context

_CHECKERS = []
_CONTEXTS = []


def _is_private(plugin):
    """bool: Check if the plugin is meant to be registered."""
    if not inspect.isclass(plugin):
        name = plugin.__class__.__name__
    else:
        name = plugin.__name__

    return name.startswith("_")


def _has_checker_interface(plugin):
    """bool: Make sure `plugin` will work with ``rez_lint``."""
    attributes = ["get_long_code", "get_order", "run"]

    for name in attributes:
        if not hasattr(plugin, name):
            return False

    return True


def _has_context_interface(plugin):
    """bool: Make sure `plugin` will work with ``rez_lint``."""
    attributes = ["get_order", "run"]

    for name in attributes:
        if not hasattr(plugin, name):
            return False

    return True


def get_checkers():
    """list[:class:`.BaseChecker`]: The plugins used to check for lint issues."""
    return list(_CHECKERS)


def get_contexts():
    """list[:class:`.BaseChecker`]: The plugins used to add data to other, checker plugins."""
    return list(_CONTEXTS)


def register_checker(checker):
    """Add a new checker plugin to ``rez_lint``.

    Args:
        checker (:class:`.BaseChecker`):
            A plugin that checks the user's Rez package for issues and
            reports them.

    Raises:
        EnvironmentError: If `checker` is already registered.
        ValueError: If `checker` is not a valid plugin.

    """
    if checker in _CHECKERS:
        raise EnvironmentError(
            'Cannot register "{checker}" because it is already registered.'
            "".format(checker=checker)
        )

    if _is_private(checker):
        raise ValueError(
            'Class "{checker}" cannot be a plugin because it is private.'
            "".format(checker=checker)
        )

    if not _has_checker_interface(checker):
        raise ValueError(
            'Class "{checker}" must inherit from BaseChecker. '
            "It is not a valid checker plugin.".format(checker=checker)
        )

    _CHECKERS.append(checker)


def register_context(context):
    """Add a new context plugin to ``rez_lint``.

    Args:
        context (:class:`.BaseContext`):
            A plugin that adds data to the context object that gets
            passed into the user's registered checker plugins.

    Raises:
        EnvironmentError: If `context` is already registered.
        ValueError: If `context` is not a valid plugin.

    """
    if context in _CONTEXTS:
        raise EnvironmentError(
            'Cannot register "{context}" because it is already registered.'
            "".format(context=context)
        )

    if _is_private(context):
        raise ValueError(
            'Class "{context}" cannot be a plugin because it is private.'
            "".format(context=context)
        )

    if not _has_context_interface(context):
        raise ValueError(
            'Class "{context}" must inherit from BaseContext. '
            "It is not a valid context plugin.".format(context=context)
        )

    _CONTEXTS.append(context)


def register_plugins(plugins):
    """Add plugins to ``rez_lint``.

    Args:
        plugins (iter[:class:`.BaseChecker` or :class:`.BaseContext`]):
            The class objects that will be added ``rez_lint``.

    Raises:
        NotImplementedError: If a plugin of unknown type is given as `plugins`.

    """
    contexts = get_contexts()
    checkers = get_checkers()

    for plugin in plugins:
        if _is_private(plugin):
            continue

        if _has_checker_interface(plugin):
            if plugin not in checkers:
                register_checker(plugin)
        elif _has_context_interface(plugin):
            if plugin not in contexts:
                register_context(plugin)
        else:
            raise NotImplementedError(
                'Plugin "{plugin}" is not a recognized type.'.format(plugin=plugin)
            )


def clear_checkers():
    """Remove all checker plugins so that :func:`get_checkers` can't access them."""
    _CHECKERS[:] = []


def clear_contexts():
    """Remove all context plugins so that :func:`get_contexts` can't access them."""
    _CONTEXTS[:] = []
