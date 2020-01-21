#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Website / URL / "world-wide-web" related functions."""


from six.moves import urllib


def is_internet_on(timeout=1):
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
    try:
        urllib.request.urlopen(
            "http://216.58.192.142",  # This is the IP address to google
            timeout=timeout,
        )
    except urllib.error.URLError:
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
