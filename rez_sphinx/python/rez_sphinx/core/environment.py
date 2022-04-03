"""Miscellaneous functions for querying the user's environment."""

import os

from . import exception


def is_publishing_enabled():
    """bool: Check if the user's current environment is capable of publishing."""
    return os.getenv("REZ_EPH_REZ_SPHINX_FEATURE_DOCBOT_PLUGIN_REQUEST", "0").endswith(
        "1"
    )


def get_publish_url(package):
    """Find the location where ``package``'s documentation will be built to.

    It's expected that the destination will be some network URL but this
    function could also return an absolute / relative path on-disk somewhere,
    potentially.

    Args:
        package (rez.package.Package):
            The source or installed Rez package to query from.

    Raises:
        PluginConfigurationError: If an expected plug-in URL could not be queried.

    Returns:
        str: The found destination.

    """
    from rez_docbot import api

    try:
        return api.get_first_versioned_view_url(package)
    except RuntimeError:
        raise exception.PluginConfigurationError(
            'rez_docbot is loaded but no configured publish URL neither globally '
            'nor from "{package.name} / {package.version}". '
            "Please add it to your rezconfig and try again.".format(
                package=package,
            ),
        )
