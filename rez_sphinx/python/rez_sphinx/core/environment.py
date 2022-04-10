"""Miscellaneous functions for querying the user's environment."""

import os

from . import exception


def is_docbot_exception(error):
    """bool: Check if ``error`` comes from :ref:`rez_docbot`."""
    try:
        from rez_docbot import api  # pylint: disable=import-outside-toplevel
    except ImportError:
        # It's disabled. Just ignore it.
        return False

    return isinstance(error, api.CoreException)


def is_publishing_enabled():
    """bool: Check if the user's current environment is capable of publishing."""
    return os.getenv("REZ_EPH_REZ_SPHINX_FEATURE_DOCBOT_PLUGIN_REQUEST", "0").endswith(
        "1"
    )


def get_publish_url(package):
    """Find the website where ``package``'s can view its documentation from.

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
    from rez_docbot import api  # pylint: disable=import-outside-toplevel

    try:
        return api.get_first_versioned_view_url(package)
    except RuntimeError:
        raise exception.PluginConfigurationError(
            "rez_docbot is loaded but no configured view URL was found "
            'globally nor from "{package.name} / {package.version}". '
            "Please add it to your rezconfig via "
            ":ref:`rez_docbot.publishers.*.view_url` "
            "and try again.".format(
                package=package,
            ),
        )


def get_all_repository_uris(package):
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
    from rez_docbot import api  # pylint: disable=import-outside-toplevel

    publishers = api.get_all_publishers(package)

    if not publishers:
        raise exception.PluginConfigurationError(
            "rez_docbot is loaded but no configured publishers were found "
            'globally nor from "{package.name} / {package.version}". '
            "Please add it to your rezconfig via "
            ":ref:`rez_docbot:rez_docbot.publishers` "
            "and try again.".format(
                package=package,
            ),
        )

    output = []

    for publisher in publishers:
        uri = publisher.get_resolved_repository_uri()
        required = publisher.is_required()

        output.append((uri, required))

    return output
