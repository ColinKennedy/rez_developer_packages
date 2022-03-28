"""A collection of functions to make writing schemas in this package easier."""

import re

import _sre
import schema
import six
from six.moves import urllib_parse

_URL_SUBDIRECTORY = re.compile(r"^[\w/]+$")
_REGEX_TYPE = type(_URL_SUBDIRECTORY)

# TODO : Make sure I don't need functions for these later. If not, simplify them
DEFAULT_AUTHENTICATION = "raw"
RAW = "raw"
FROM_FILE = "from_file"


def _validate_callable(item):
    """Check if ``item`` is a callable object (like a function or class).

    Args:
        item (callable): Something to check.

    Raises:
        ValueError: If ``item`` isn't callable.

    Returns:
        callable: The original ``item``.

    """
    if callable(item):
        return item

    raise ValueError('Item "{item}" isn\'t a callable function.'.format(item=item))


def _validate_non_empty_str(item):
    """Ensure ``item`` is a string with at least some text.

    Args:
        item (str): An object to check.

    Raises:
        ValueError: If ``item`` isn't a string or it is an empty string.

    Returns:
        str: The original ``item``.

    """
    if not isinstance(item, six.string_types):
        raise ValueError('Item "{item!r}" is not a string.'.format(item=item))

    if not item:
        raise ValueError("String cannot be empty.")

    return item


def _validate_regex(item):
    """Check if ``item`` is a regular expression.

    Args:
        item (_sre.SRE_Pattern): The object to check.

    Raises:
        ValueError: If ``item`` isn't a regular expression.

    Returns:
        _sre.SRE_Pattern: The original ``item``.

    """
    if isinstance(item, _REGEX_TYPE):
        return item

    raise ValueError(
        'Item "{item}" must be a compiled regex pattern.'.format(item=item)
    )


def _validate_url(item):
    """Check if ``item`` is a URL / URI.

    Args:
        item (str): A website or similar URI. Like "http://www.foo.bar".

    Raises:
        ValueError: If ``item`` isn't a URL / URI.

    Returns:
        str: The original, unaltered ``item``.

    """
    result = urllib_parse.urlparse(item)

    if all((result.scheme, result.netloc)):
        return item

    raise ValueError('Item "{item}" is not a valid URL.'.format(item=item))


def _validate_url_subdirectory(item):
    """Check if ``item`` describes a URL sub-directory.

    e.g. The "inner/folder" part of "www.foo.bar/inner/folder"

    Important:
        This is a **URL** subdirectory, not a on-disk sub-directory. Window
        backlashes are not allowed.

    Args:
        item (str): An inner folder to check.

    Raises:
        ValueError: If ``item`` isn't a sub-directory.

    """
    if _URL_SUBDIRECTORY.match(item):
        return item

    raise ValueError(
        'Item "{item}" is invalid. It must match "{_URL_SUBDIRECTORY.pattern}".'.format(
            item=item, _URL_SUBDIRECTORY=_URL_SUBDIRECTORY
        )
    )


NON_EMPTY_STR = schema.Use(_validate_non_empty_str)

DEFAULT_PUBLISH_PATTERN = "{package.version.major}.{package.version.minor}"
PUBLISH_PATTERNS = schema.Or(
    _validate_regex, NON_EMPTY_STR
)  # TODO : Consider making these more strict in the future

CALLABLE = schema.Use(_validate_callable)

URL = schema.Use(_validate_url)
URL_SUBDIRECTORY = schema.Use(_validate_url_subdirectory)
# SSH = schema.Use(_validate_ssh)  TODO Add this later
