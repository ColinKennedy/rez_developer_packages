#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The module that contains the abstract class for submitting pull requests."""

import abc
import collections

PullRequestDetails = collections.namedtuple(
    "PullRequestDetails", "url source destination"
)


class BaseAdapter(object):
    """An abstract class that submits pull requests for the user.

    This class must be subclassed and extended (e.g. to support GitHub
    or bitbucket, for example).

    """

    @staticmethod
    @abc.abstractmethod
    def is_valid_url(url):
        """Check if a site address is a valid remote git URL.

        Examples:
            git@github.org:foo/bar.git
            https://github.com/foo/bar.git

        Args:
            url (str): The website / address to a repository.

        Returns:
            bool: If `url` is a git remote repository.

        """
        return False

    @staticmethod
    @abc.abstractmethod
    def create_pull_request(title, body, pull_request_data, user_data="", assignee=""):
        """Make a pull request to the remote, using the given information.

        It's recommended to always provide `user_data` because querying
        data from external sites like GitHub can be extremely slow.

        Args:
            title (str): The subject line of the pull request.
            body (str): A description of the pull request's changes. Make it good!
            pull_request_data (:attr:`.PullRequestDetails`):
                The URL to a hosted Git repository, the source (feature)
                branch to use for the pull request and the destination
                branch (usually master) for it to merge into.
            user_data (str, optional): A file path that is used to read cached user login,
                e-mail, and name information. If no information is given
                then it is queried before pull requests are created.
            assignee (str, optional):
                The name of a GitHub user to add to created PRs. Default: "".

        """
        pass
