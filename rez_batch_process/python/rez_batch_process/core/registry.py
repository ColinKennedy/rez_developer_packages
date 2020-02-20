#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The module that controls how and why a valid Rez package may not need documentation.

By default, the registered plugins will skip a Rez package if it is not
a Python package or already has documentation.

"""

from .plugins import command, conditional

_COMMANDS = {"shell": command.RezShellCommand}
_PLUGINS = {"shell": conditional.get_default_latest_packages}


def get_command(name):
    """Find the adapter class needed for the ``rez_batch_process`` CLI to run.

    Args:
        name (str): An identifier used to find the correct command class.

    Returns:
        :class:`.BaseCommand` or NoneType: The found command.

    """
    return _COMMANDS.get(name)


def get_command_keys():
    """set[str]: The available commands that are registered to ``rez_batch_process``."""
    return set(_COMMANDS.keys())


def get_plugin_keys():
    """set[str]: All of the functions, by-name, that are used to find Rez packages."""
    return set(_PLUGINS.keys())


def get_package_finder(name):
    """Get a function that's used to find Rez packages.

    Raises:
        ValueError: If `name` is not registered.

    Returns:
        callable[list[str]] -> tuple[:class:`rez.packages_.Package`, list, list]:
            A function that takes Rez package paths as its only argument
            and returns a list of Rez packages that will be processed by ``rez_batch_process``,
            any package that's invalid, and any package that should be skipped
            (and thus, not processed).

    """
    if name not in _PLUGINS:
        raise ValueError(
            'Command "{name}" has no registered package function.'.format(name=name)
        )

    return _PLUGINS[name]


def clear_command(name):
    """Remove `name` from the list of registered command adapters.

    Args:
        name (str): An identifier used to find the correct command class.

    Raises:
        ValueError: If there is no registered adapter for `name`.

    """
    if name not in _COMMANDS:
        raise ValueError(
            'Name "{name}" is not registered so it cannot be cleared. Options were "{options}".'
            "".format(name=name, options=sorted(_COMMANDS.keys()))
        )

    del _COMMANDS[name]


def clear_plugin(name):
    """Remove `name` from the list of registered plugin adapters.

    Args:
        name (str): An identifier used to find the correct plugin class.

    Raises:
        ValueError: If there is no registered adapter for `name`.

    """
    if name not in _PLUGINS:
        raise ValueError(
            'Name "{name}" is not registered so it cannot be cleared. Options were "{options}".'
            "".format(name=name, options=sorted(_PLUGINS.keys()))
        )

    del _PLUGINS[name]


def register_command(name, adapter, override=False):
    """Add `adapter` with an identifier of `name` to this available list of commands.

    Args:
        name (str):
            An identifier used to find the correct command class.
        adapter (:class:`.BaseCommand`):
            The class used to run some command.
        override (bool, optional):
            If True and `name` is already registered, replace the
            existing adapter. False, raise an exception. Default is False.

    Raises:
        ValueError:
            If `name` is already a registered command and `override` is
            not set to True.

    """
    if not override and name in _COMMANDS:
        raise ValueError('Name "{name}" is already registered.'.format(name=name))

    _COMMANDS[name] = adapter


def register_plugin(name, plugin, override=False):
    """Add `adapter` with an identifier of `name` to this available list of plugins.

    Args:
        name (str):
            An identifier used to find the correct plugin class.
        adapter (:class:`.BasePlugin`):
            The class used to check for some kind of issue with a Rez
            package. If the adapter finds some kind of problem, the Rez
            package is skipped and a registered command will not be run.
        override (bool, optional):
            If True and `name` is already registered, replace the
            existing adapter. False, raise an exception. Default is False.

    Raises:
        ValueError:
            If `name` is already a registered plugin and `override` is
            not set to True.

    """
    if not override and name in _PLUGINS:
        raise ValueError('Name "{name}" is already registered.'.format(name=name))

    _PLUGINS[name] = plugin
