#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""A module to help query and and serialize a list of GitHub users."""

import json
import sys

from . import github_link


def write_cache(path, token, base_url="", verify=False, maximum=sys.maxsize):
    """Serialize a list of GitHub users to-disk.

    Reference:
        https://help.github.com/en/github/authenticating-to-github/creating-a-personal-access-token-for-the-command-line

    Args:
        path (str):
            The absolute or relative path to a JSON file which will be written to.
        token (str):
            The GitHub authentication token that will be used to get user data.
            See the reference link for details.
        base_url (str, optional):
            The API URL that goes with the given `token`. If you're not
            using GitHub Enterprise, just leave this parameter blank.
            Default: "".
        verify (bool, optional):
            If True, require a valid SSL certificate in private If
            networks. If False, accept all external SSL certificates.
            Default is True.

    """
    users = github_link.get_all_users(
        token, base_url=base_url, verify=verify, maximum=maximum, write=False
    )

    data = []

    for user in users:
        data.append(
            {
                "email": user.email or "",
                "bio": user.bio or "",
                "login": user.login,
                "name": user.name or "",
            }
        )

    with open(path, "w") as handler:
        json.dump(data, handler)
