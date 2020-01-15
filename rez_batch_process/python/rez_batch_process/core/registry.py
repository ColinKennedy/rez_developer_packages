#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The module that controls how and why a valid Rez package may not need documentation.

By default, the registered plugins will skip a Rez package if it is not
a Python package or already has documentation.

"""

from .plugins import command, conditional

_PLUGINS = [conditional.NonPythonPackage, conditional.HasDocumentation]
_COMMAND = command.RezShellCommand


def get_command():
    """:class:`.BaseCommand`: The command that will be used by this CLI when run."""
    return _COMMAND


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
