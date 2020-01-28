#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Website / URL / "world-wide-web" related functions."""

import socket

from six.moves import urllib


def is_internet_on(timeout=2):
    """Check if the user has connection to an external website.

    Reference:
        https://stackoverflow.com/a/3764660/3626104.

    Args:
        timeout (int, optional):
            Number of seconds to wait before giving up on a connection.
            Default: 1.

    Returns:
        bool: If there is no network connection.

    """
    # Reference: https://stackoverflow.com/questions/8763451
    known_exceptions = (
        urllib.error.HTTPError,  # old-style timeout
        socket.timeout,  # Python 3 exception for timeouts
        urllib.error.URLError,
    )

    try:
        urllib.request.urlopen(
            "http://216.58.192.142",  # This is the IP address to google
            timeout=timeout,
        )
    except known_exceptions:
        return False

    return True


def is_url_reachable(url, timeout=1):
    """Check if a URL exists and can be accessed.

    Args:
        url (str):
            The http / ftp / etc address.
        timeout (int, optional):
            Number of seconds to wait before giving up on a connection.
            Default: 1.

    Returns:
        bool: If `url` sends an expected response.

    """
    try:
        return (
            urllib.request.urlopen(url, timeout=timeout).getcode() == 200
        )  # `200` means "website found
    except urllib.error.URLError:
        return False
