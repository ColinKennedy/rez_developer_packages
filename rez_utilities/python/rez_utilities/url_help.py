#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""A module for querying rez-help from Rez packages."""

import fnmatch
import itertools
import logging

from python_compatibility import website
from six.moves import urllib

from .plugins import registry

_EXPECTED_API_LABELS = frozenset(
    ("api documentation", "api", "api-documentation", "api_documentation")
)
_LOGGER = logging.getLogger(__name__)


def _is_online():
    """Check if the user has internet access.

    Reference:
        https://stackoverflow.com/a/3764660/3626104

    Returns:
        bool: If the Internet is enabled.

    """
    try:
        return urllib.request.urlopen("http://216.58.192.142", timeout=1)
    except urllib.error.URLError:
        return False

    return True


def _get_url(text):
    """Find the website URL from some Rez package help command.

    In Rez, help documentation can be written as a raw URL, like
    "https://google.com" but you can also write it as a command, such as
    "firefox https://google.com". This function is designed to get just
    the URL, no matter what format is used.

    Args:
        text (str): The raw Rez package information.

    Returns:
        str: The found URL.

    """
    return text.split(" ")[-1]


def _find_known_documentation(package):
    """Get documentation for a Rez package, assuming the package is a verifiable source.

    In general, Rez packages should define their own help documentation
    URLs. Because of that, this function should be seen as a "last
    resort" instead of the preferred way of finding documentation.

    That said, some Rez packages (like ones that you generate using
    ``rez-bind`` are generic but also don't have URL documentation
    links. So we use this function for packages like those).

    Note:
        This function will prefer to find exact, versioned documentation
        before getting the "latest" documentation of any Rez package.

    Args:
        package (:class:`rez.developer_package.DeveloperPackage`):
            The Rez package that will be used to search for documentation.

    Returns:
        str: The found documentation URL, if any.

    """

    def _get_python_url(package):
        if int(str(package.version.major)) == 2:
            return "https://docs.python.org/2/index.html"

        version = package.version
        base = "https://docs.python.org/{version.major}.{version.minor}/index.html"

        return base.format(version=version)

    def _get(item):
        """str: Return the given item."""
        return item

    known = {
        "Click": "https://click.palletsprojects.com",
        "Flask": "https://flask.palletsprojects.com",
        "ItsDangerous": "https://itsdangerous.palletsprojects.com",
        "Jinja2": "https://jinja.palletsprojects.com",
        "MarkupSafe": "https://markupsafe.palletsprojects.com",
        "Werkzeug": "https://werkzueg.palletsprojects.com",
        "python": _get_python_url,
        "rez": "",
        "setuptools": "https://setuptools.readthedocs.io",
        "six": "https://six.readthedocs.io",
    }

    item = known[package.name]

    if callable(item):
        return item(package)

    return item


def _find_rez_api_documentation(package):
    """Check for API documentation by reading a Rez package's ``help`` attribute.

    Rez packages may not define a help attribute and it also may not
    actually show API documentation. If either scenario happens, this
    function returns nothing.

    Args:
        package (:class:`rez.developer_package.DeveloperPackage`):
            The Rez package that will be used to search for documentation.

    Returns:
        str: The found API documentation, if any.

    """
    for (label, url), name in itertools.product(
        get_help_urls(package), _EXPECTED_API_LABELS
    ):
        if name in label:
            return url

    return ""


def _find_rez_documentation(package, filters=frozenset(("*",))):
    """Find Sphinx documentation from a Rez package.

    Args:
        package (:class:`rez.developer_package.DeveloperPackage`):
            The package to check for some Sphinx-related documentation.
            Return the first valid match.
        filters (list[str]):
            Glob match patterns to use for searching for documentation.
            If the Rez documentation's label matches at least one
            pattern, it will be searched for Sphinx documentation. The
            Default is {"*", }, which will allow any Rez documentation.

    Returns:
        str: The found Sphinx-compatible documentation, if any exists.

    """

    def _get_inventory_file(url):
        suffix = "/objects.inv"

        if not url.endswith(suffix):
            url += suffix

        if website.is_url_reachable(url):
            return url

        return ""

    for label, url in get_help_urls(package):
        if any(fnmatch.fnmatch(label, pattern) for pattern in filters):
            inventory = _get_inventory_file(url)

            if inventory:
                return inventory

    return ""


def is_url_reachable(url):
    """bool: Check if a URL exists and can be accessed."""
    known_exceptions = (
        # Happens if the URL syntax is valid but the URL is not reachable
        urllib.error.URLError,
        # Happens if you use a totally invalid syntax. e.g. "asdf"
        ValueError,
    )

    try:
        return (
            urllib.request.urlopen(url, timeout=1).getcode() == 200
        )  # `200` means "website found
    except known_exceptions:
        return False


def get_help_urls(package):
    """Find every help item that doesn't point to a valid URL.

    Args:
        package (:class:`rez.developer_package.DeveloperPackage`):
            The user package description that may have URLs inside of
            it. If URLs exist, check each one for any potential issues.

    Returns:
        list[tuple[int, str]]:
            The help command label and URL for each invalid URL found.

    """
    return [(label, _get_url(command)) for label, command in package.help or []]


def get_invalid_help_urls(package):
    """Find every help item that doesn't point to a valid URL.

    Args:
        package (:class:`rez.developer_package.DeveloperPackage`):
            The user package description that may have URLs inside of
            it. If URLs exist, check each one for any potential issues.

    Returns:
        set[tuple[int, str, str]]:
            The position, help command label, and URL for each invalid URL found.

    """
    invalids = set()

    for index, (label, command) in enumerate(package.help or []):
        url = _get_url(command)

        if not is_url_reachable(url):
            invalids.add((index, label, command))

    return invalids


def find_api_documentation(package):
    """Get the URL to a Rez package's API documentation, using any available means.

    This function will first try to find the documentation by "common"
    documentation conventions and start to "guess" if nothing is
    immediately found.

    Args:
        package (:class:`rez.developer_package.DeveloperPackage`):
            The user package which will be used to search for API documentation.

    Returns:
        str: The found API documentation URL, if any.

    """
    try:
        return _find_known_documentation(package)
    except KeyError:
        pass

    url = _find_rez_api_documentation(package)

    if url:
        return url

    templates = registry.get_help_url_templates()

    for template in templates:
        url = template.format(package=package)

        if website.is_url_reachable(url):
            return url

    _LOGGER.debug('Package "%s" has no known Sphinx documentation URL.', package.name)

    return ""


def find_package_documentation(package):
    """Find Sphinx documentation from a Rez package.

    Args:
        package (:class:`rez.developer_package.DeveloperPackage`):
            The user package which will be used to search for API documentation.

    Returns:
        str: The found API documentation URL, if any.

    """
    return _find_rez_documentation(package)
