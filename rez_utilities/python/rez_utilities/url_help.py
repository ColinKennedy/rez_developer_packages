#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""A module for querying rez-help from Rez packages."""

import fnmatch
import logging

import six
from six.moves import urllib

_EXPECTED_API_LABELS = frozenset(
    ("api documentation", "api", "api-documentation", "api_documentation")
)
_LOGGER = logging.getLogger(__name__)


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

    help_ = package.help or []

    if isinstance(help_, six.string_types):
        # The user can give a list of list of strings or just a single string
        # Reference: https://github.com/nerdvegas/rez/wiki/Package-Definition-Guide#help
        #
        help_ = [["", help_]]

    for index, (label, command) in enumerate(help_):
        url = _get_url(command)

        if not is_url_reachable(url):
            invalids.add((index, label, command))

    return invalids


def find_api_documentation(package):
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

    try:
        item = known[package.name]
    except KeyError:
        return ""

    if callable(item):
        return item(package)

    return item


def find_package_documentation(package, filters=frozenset(("*",))):
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

    def _sort_by_label(item):
        label, _ = item

        all_labels = get_common_documentation_help_labels()
        count = len(all_labels)

        for index, label_ in enumerate(all_labels):
            if label_ == label:
                return index

        guess_conditions = [
            "api" in label,
            "api" in label.lower(),
            "documentation" in label,
            "documentation" in label.lower(),
            "docs" in label,
            "docs" in label.lower(),
        ]

        for index, condition in enumerate(guess_conditions):
            if condition:
                return count + index + 1

        return count + len(guess_conditions)  # Put the term somewhere at the end

    for label, url in sorted(get_help_urls(package), key=_sort_by_label):
        if any(fnmatch.fnmatch(label, pattern) for pattern in filters):
            return url

    return ""


def get_common_documentation_help_labels():
    """tuple[str]: Typical "documentation"-related keys that you'd expect used for rez-help."""
    return (
        "api_documentation",
        "user_documentation",
        "developer_documentation",
        "api",
        "user",
        "developer",
    )
