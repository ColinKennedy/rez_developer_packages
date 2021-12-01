"""The functions for finding and loading interfaces which build documentation."""

import logging
import os

from . import sphinx
from ...core import core_exception

_KNOWN_PLUGINS = {
    sphinx.Plugin.get_name(): sphinx.Plugin,
}
_USER_REGISTERED_PLUGINS = dict()

_LOGGER = logging.getLogger(__name__)


def get_plugin(name):
    """Find the plug-in which matches `name`.

    Args:
        name (str): The plug-in identifier. e.g. "sphinx".

    Raises:
        :class:`.NoPluginFound`: If `name` doesn't match a registered plug-in.

    Returns:
        :class:`.BuilderPlugin`: The found plug-in.

    """
    try:
        return _KNOWN_PLUGINS[name]
    except KeyError:
        _LOGGER.debug('Name "%s" is not a known plugin. Now trying user-plugins.')

    try:
        _USER_REGISTERED_PLUGINS[name]
    except KeyError:
        raise core_exception.NoPluginFound(
            'Plug-in "{name}" does not exist. The options were, "{options}".'.format(
                name=name,
                options=sorted(get_plugin_names())
            )
        )


def get_plugin_names():
    """set[str]: Get every plug-in which can be used to build documentation."""
    names = set(_KNOWN_PLUGINS.keys())
    names.update(_USER_REGISTERED_PLUGINS.keys())

    return names


def register_user_plugins():
    """Find and load any builder / publisher classes and add them to `rez_docbot`."""
    text = os.getenv("REZ_DOCBOT_BUILDER_PLUGINS", "")

    if text:
        modules = text.split(os.pathsep)
    else:
        modules = []

    for module in modules:
        raise NotImplementedError("Need to import here")
