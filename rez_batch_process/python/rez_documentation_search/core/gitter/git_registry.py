#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""A module that lets the user control how pull requests are submitted for git repositories."""

from . import github_link

_ADAPTERS = [github_link.GithubAdapter]


def get_remote_adapter(package, url, token, fallback_reviewers=None, base_url=""):
    """Find a class that should create pull requests for the given package + URL.

    Args:
        package (:class:`rez.packages_.Package`):
            The Rez package which is queried to find find information
            for the pull request. For example, who to add as reviewers.
        url (str):
            The URL to the repository that a pull request will be made for.
        token (str):
            The authentication token that will be used to connect to the
            remote source. e.g. GitHub.
        fallback_reviewers (list[str], optional):
            The usernames of people that will be added to a review in
            case not enough maintainers in the Rez package + repository
            could be found to fill the review.
        base_url (str, optional):
            The API url that is used if the user needs to access
            a non-standard remote location. For example, if the
            user is working in GitHub Enterprise and not regular
            GitHub, they'll need to provide a `base_url` to the
            GitHub Enterprise URL to authenticate. Default: "".

    Returns:
        :class:`.BaseAdapter` or NoneType: The found class, if any.

    """
    if not fallback_reviewers:
        fallback_reviewers = []

    for adapter in _ADAPTERS:
        if adapter.is_valid_url(url):
            return adapter(package, token, fallback_reviewers=fallback_reviewers, base_url=base_url)

    return None
