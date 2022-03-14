"""A module to make :ref:`rez_sphinx` configuration options easier to parse."""

import schema
from rez.utils import formatting


def _validate_request(text):
    """Check if ``text`` matches a Rez package request.

    Args:
        text (str): A request like ``"python-1+<2"``, ``"some_package==1.2.3", etc.

    Returns:
        str: The original, unmodified text.

    """
    formatting.PackageRequest(text)

    return text


REQUEST_STR = schema.Use(_validate_request)
