#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The main module that controls how pull requests are sent to GitHub."""

import collections
import itertools
import json
import logging
import re
import sys
import tempfile

import github
import github3
from github3 import exceptions as github3_exceptions

from . import base_adapter

try:
    from functools import lru_cache  # python 3
except ImportError:
    from backports.functools_lru_cache import lru_cache  # python 2


_CONVENTIONS = frozenset(
    (
        # https://github.com/foo/bar.git
        re.compile(
            r"""
            (?:(?P<protocol>http|https)://)?
            (?:www\.)?
            (?P<base>.+)/(?P<owner>[\w\-_]+)/(?P<repository_name>[\w\-_]+)
            (?:\.git)?$
            """,
            re.VERBOSE,
        ),
        # git@github.org:foo/bar.git
        re.compile(
            r"""
            (?P<protocol>git)@
            (?P<base>.+):(?P<owner>[\w\-_]+)/(?P<repository_name>[\w\-_]+)
            (?:\.git)?$
            """,
            re.VERBOSE,
        ),
    )
)
_LOGGER = logging.getLogger(__name__)
_ParsedRepository = collections.namedtuple(
    "_ParsedRepository", "protocol base owner name"
)
_User = collections.namedtuple("_User", "login name email bio")


class GithubAdapter(base_adapter.BaseAdapter):
    """The class that submits pull requests to GitHub."""

    def __init__(
        self, package, token, fallback_reviewers=None, base_url="", verify=True
    ):
        """Create this instance and store Rez / GitHub information.

        Args:
            package (:class:`rez.packages_.Package`):
                The Rez package which is queried to find find
                information for the pull request. For example, who to
                add as reviewers.
            token (str): The authentication login that will be
                used to connect to GitHub.
            fallback_reviewers (list[str], optional): The GitHub users
                that will be added to a review in case not enough
                maintainers in the Rez package + repository could be
                found to fill the review.
            base_url (str, optional): The API url that is used if the
                user needs to access a non-standard remote location. For
                example, if the user is working in GitHub Enterprise and
                not regular GitHub, they'll need to provide a `base_url`
                to the GitHub Enterprise URL to authenticate. Default: "".
            verify (bool, optional): If True, require a valid SSL
                certificate in private If networks. False, accept all
                external SSL certificates. Default is True.

        """
        super(GithubAdapter, self).__init__()

        if not fallback_reviewers:
            fallback_reviewers = []

        self._base_url = base_url
        self._fallback_reviewers = fallback_reviewers
        self._package = package
        self._token = token
        self._user = get_user(token, url=base_url, verify=verify)
        self._verify = verify

    def _get_reviewers(self, repository, package_maintainers, fallback_reviewers=None):
        """Get the GitHub users that will be added to the pull request.

        The logic does like this

        - Prioritize authors written in each Rez package
        - The use the repository owner
        - If there are still people missing, find repository contributors
        - If there still aren't enough people to fill 3 slots, use the
          fallback reviewers list (if it exists) get 3-or-more people on the
          review.

        Args:
            repository (:class:`github3.github.GitHub`):
                The GitHub instance that is used to get users to add to
                the pull request.
            package_maintainers (list[str]):
                The GitHub login names written in the Rez package's list
                of authors. This list may be incomplete if the written
                Rez package author could not be "linked" to a GitHub login.
            fallback_reviewers (list[str], optional):
                The usernames of people are added to reviews in case
                no reviewers could be found for the Rez package or the
                repository. Default is None.

        Returns:
            list[str]: The GitHub logins of each person to add the pull request.

        """
        if not fallback_reviewers:
            fallback_reviewers = []

        authors = package_maintainers
        owner = repository.owner.login

        if owner not in authors:
            authors.append(owner)

        for user in repository.contributors():
            login = user.login

            if login not in authors:
                authors.append(login)

        authors += fallback_reviewers

        return authors

    @staticmethod
    def is_valid_url(url):
        """Check if a site address is a valid "GitHub" URL.

        Examples include:

        - https://github.com/foo/bar.git
        - http://github.com/foo/bar.git
        - git@github.org:foo/bar.git

        Args:
            url (str): The website / address to a GitHub repository.

        Returns:
            bool: If `url` is a GitHub repository.

        """
        link = _get_github_url_data(url)

        if not link:
            return False

        return "github" in link.base.lower()

    def create_pull_request(
        self, title, body, pull_request_data, user_data="", assignee=""
    ):
        """Make a pull request to GitHub, using the given information.

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
        if not user_data:
            user_data = get_all_users(
                self._token, self._base_url, verify=self._verify, write=True
            )
        else:
            user_data = _read_users_from_cache(user_data)

        data = _get_github_url_data(pull_request_data.url)
        repository = self._user.repository(data.owner, data.name)

        package_maintainers = _convert_to_github_user_names(
            self._package.authors or [], user_data
        )
        reviewers = self._get_reviewers(
            repository, package_maintainers, fallback_reviewers=self._fallback_reviewers
        )

        try:
            pull_request = repository.create_pull(
                title, pull_request_data.destination, pull_request_data.source, body
            )
        except github3_exceptions.UnprocessableEntity as error:
            _LOGGER.warning(
                'Pull request failed. This may happen if "%s" already has a pull request '
                'but fould happen for basically any reason. Check output "%s" for details.',
                pull_request_data.source,
                error.errors,
            )

            if error.code != 422:
                _LOGGER.exception(
                    'Pull request was prevented because of this error, "%s".', error
                )

                raise

        # Add another parameter for an optional assignee, here
        if assignee:
            try:
                assignee_ = next(user for user in user_data if user.login == assignee)
            except StopIteration:
                _LOGGER.exception('No user could be found for "%s".', assignee)
            else:
                pull_request.assignees = [assignee_]

        # This next line adds the reviewers to the already-created-pull
        # request. It's an awkward syntax but oh well.
        #
        pull_request.create_review_requests(reviewers=reviewers)


def _convert_to_github_user_names(package_authors, github_users):
    """Change the Rez package raw author list into GitHub logins.

    There's no established convention for Rez package author names. Some
    people put their personal login, other's put their e-mail, others
    write their full name.

    This function's job is to reason, as best as it can, what that
    person's GitHub login could be.

    Important:
        This function is not guaranteed to return a result for
        everything written in `package_authors`. It will only return a
        result if the function is reasonably confident that a match was
        found.

    Args:
        package_authors (list[str]):
            The people responsible for the Rez package.
        github_users (list[:attr:`_User`]):
            Name, e-mail, login, etc details about every GitHub user.
            This will be used as a reference to get actual GitHub user names.

    Returns:
        list[str]: The found GitHub user logins.

    """
    output = []

    for author in package_authors:
        for user in github_users:
            if user.login in author or user.name in author or author in user.bio:
                output.append(user.login)

                break
        else:
            _LOGGER.warning(
                'Author "%s" could not be converted into a GitHub user.', author
            )

    return output


def _get_github_url_data(url):
    """Find information such as repository owner, repository name, etc from a GitHub URL.

    Args:
        url (str): The website / address which may be a GitHub-related URL.

    Returns:
        :attr:`_ParsedRepository` or NoneType: The found GitHub information, if any.

    """
    for expression in _CONVENTIONS:
        match = expression.match(url)

        if match:
            data = match.groupdict()

            return _ParsedRepository(
                data["protocol"], data["base"], data["owner"], data["repository_name"]
            )

    return None


@lru_cache()
def _read_users_from_cache(path):
    """Parse a set of "cached_users" representing GitHub login data and return them.

    See Also:
        :func:`get_all_users`

    Args:
        path (str):
            An absolute path to a JSON file to read from. It must
            contain 4 keys, "login", "name", "email", and "bio".
            All things that can be queried and retrieved using
            :func:`get_all_users`.


    Returns:
        list[:attr:`_User`]: The found users.

    """
    output = []

    with open(path, "r") as handler:
        for user in json.load(handler):
            output.append(
                _User(user["login"], user["name"], user["email"], user["bio"])
            )

    return output


def _write_user_data_cache(users):
    """Serialize GitHub user data to JSON and write it to a file.

    Args:
        users (list[dict[str, str]]): The GitHub user data to serialize.
            "email" (str): The website address to reach this person.
            "bio" (str): A user description that people sometimes write in GitHub.
                         Most of the time, this attribute will not be useful. But you never know!
            "login" (str): The GitHub username.
            "name" (str): The display name (usually first and last name) of the person.

    """
    with tempfile.NamedTemporaryFile(suffix=".json", mode="w") as handler:
        json.dump(users, handler)

    _LOGGER.info(
        'GitHub users were cached and dumped to "%s". '
        'Re-run your command using "--cached-users %s" to use the cache.',
        handler.name,
        handler.name,
    )


@lru_cache()
def get_all_users(token, base_url="", verify=True, maximum=sys.maxsize, write=False):
    """Find every GitHub user.

    Warning:
        This function is cached but it can be VERY slow to run. Exercise
        caution. Use "cached_users" instead of querying from this
        function, whenever possible.

    Reference:
        https://help.github.com/en/github/authenticating-to-github/creating-a-personal-access-token-for-the-command-line

    See Also:
        :func:`_read_users_from_cache`

    Args:
        token (str):
            The GitHub authentication token that will be used to get user data.
        base_url (str, optional):
            The API URL that goes with the given `token`. If you're not
            using GitHub Enterprise, just leave this parameter blank.
        verify (bool, optional):
            If True, require a valid SSL certificate in private If
            networks. If False, accept all external SSL certificates.
            Default is True.

    Returns:
        list[:attr:`_User`]: The found, public GitHub users.

    """
    if base_url:
        # PyGitHub expects a URL to end with a special suffix
        # Reference: https://pygithub.readthedocs.io/en/latest/introduction.html#very-short-tutorial
        #
        enterprise_suffix = "/api/v3"

        if not base_url.endswith(enterprise_suffix):
            base_url = base_url.rstrip("/") + enterprise_suffix

        accessor = github.Github(login_or_token=token, base_url=base_url, verify=verify)
    else:
        accessor = github.Github(login_or_token=token, verify=verify)

    users = list(itertools.islice(accessor.get_users(), maximum))
    output = []

    for user in users:
        output.append(
            {
                "email": user.email or "",
                "bio": user.bio or "",
                "login": user.login,
                "name": user.name or "",
            }
        )

    if write:
        _write_user_data_cache(output)

    return [
        _User(data["login"], data["name"], data["email"], data["bio"])
        for data in output
    ]


@lru_cache()
def get_user(token, url="", verify=True):
    """Authenticate using a GitHub token and return the instance.

    Args:
        token (str):
            The GitHub authentication token that will be used to get user data.
        base_url (str, optional):
            The API URL that goes with the given `token`. If you're not
            using GitHub Enterprise, just leave this parameter blank.
        verify (bool, optional):
            If True, require a valid SSL certificate in private If
            networks. If False, accept all external SSL certificates.
            Default is True.

    Returns:
        :class:`github3.github.GitHub`: The found GitHub connection.

    """
    if url:
        accessor = github3.enterprise_login(token=token, url=url)
        accessor.session.verify = verify

        return accessor

    return github3.login(token=token)
