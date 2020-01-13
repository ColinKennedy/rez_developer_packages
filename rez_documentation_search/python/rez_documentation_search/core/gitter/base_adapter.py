#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The module that contains the abstract class for submitting pull requests."""

import abc


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
    def create_pull_request(url, title, body, source, destination, user_data=""):
        """Make a pull request to the remote, using the given information.

        It's recommended to always provide `user_data` because querying
        data from external sites like GitHub can be extremely slow.

        Args:
            url (str): The URL to the repository that a pull request will be made for.
            title (str): The subject line of the pull request.
            body (str): A description of the pull request's changes. Make it good!
            source (str): (Usually) A feature branch that will merge into master.
            destination (str): The branch to merge into. Usually "master" or "develop".
            user_data (str, optional): A file path that is used to read cached user login,
                e-mail, and name information. If no information is given
                then it is queried before pull requests are created.

        """
        pass
