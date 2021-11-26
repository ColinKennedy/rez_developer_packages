import logging
import os

from . import sphinx

_KNOWN_PLUGINS = {
    sphinx.Plugin.get_name(): sphinx.Plugin,
}
_USER_REGISTERED_PLUGINS = dict()

_LOGGER = logging.getLogger(__name__)


def get_plugin(name):
    try:
        return _KNOWN_PLUGINS[name]
    except KeyError:
        _LOGGER.debug('Name "%s" is not a known plugin. Now trying user-plugins.')

    try:
        _USER_REGISTERED_PLUGINS[name]
    except KeyError:
        raise core_exception.NoPluginFound(
            'Plug-in "{name}" does not exist. The options were, "{options}".'.format(
                options=sorted(get_allowed_plugins())
            )
        )


def get_allowed_plugins():
    names = set(_KNOWN_PLUGINS.keys())
    names.update(_USER_REGISTERED_PLUGINS.keys())

    return sorted(names)


def register_user_plugins():
    text = os.getenv("REZ_DOCBOT_BUILDER_PLUGINS", "")

    if text:
        modules = text.split(os.pathsep)
    else:
        modules = []

    for module in modules:
        raise ValueError('Need to import here')
