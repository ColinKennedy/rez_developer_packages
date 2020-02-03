#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The module that controls how and why a valid Rez package may not need documentation.

By default, the registered plugins will skip a Rez package if it is not
a Python package or already has documentation.

"""

from .plugins import command, conditional

_PLUGINS = [conditional.NonPythonPackage, conditional.HasDocumentation]

_COMMANDS = {
    "shell": command.RezShellCommand,
}


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


def get_skip_plugins():
    """Find the objects that determine whether to skip a Rez package.

    By default, the registered plugins will skip a Rez package if it is
    not a Python package or already has documentation.

    Returns:
        list[:class:`.BasePlugin`]:
            The plugins that will be used to find out if the Rez package
            needs documentation.

    """
    return _PLUGINS


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
            ''.format(name=name, options=sorted(_COMMANDS.keys())))

    del _COMMANDS[name]


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
