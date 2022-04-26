"""A collection of functions to make writing schemas in this package easier."""

import io
import json
import os
import re

import schema
import six
from git.repo import base
from rez_utilities import finder
from six.moves import urllib_parse

_SSH_EXPRESSION = re.compile(r"^git\@[\w_\.]+:(?P<group>.+)(?:/(?P<repository>.+))")
_URL_SUBDIRECTORY = re.compile(r"^[\w/{}\.]+$")  # Allow {}s so we can do {package.name}
_REGEX_TYPE = type(_URL_SUBDIRECTORY)

ORIGINAL_TEXT = "original"

_URL_SUBDIRECTORY_SEPARATOR = ""
GROUP = "group"
REPOSITORY = "repository"

_GIT_DEFAULT_REMOTE_NAME = "origin"

# Reference: https://www.infoq.com/news/2021/04/github-new-token-format/
#
# Example "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"
#
_GITHUB_PERSONAL_ACCESS_TOKEN = re.compile(r"\w+_[a-zA-Z0-9]")


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


def _validate_defer_git_repository(item):
    """Allow the remote repository to be queried at runtime, using a Rez package.

    Args:
        item (None):
            Indicate whether "defer repository evaluation" is enabled.

    Raises:
        ValueError:
            If ``item`` is not None, it means "defer repository evaluation" is
            not enabled.

    Returns:
        callable[rez.packages.Package] -> str:
            A function which, given some Rez package, gets the push repository
            URL where the package is meant to publish to.

    """

    def _get_preferred_remote(repository):
        remotes = repository.remotes

        if not remotes:
            raise RuntimeError(
                'Repository "{repository}" has no remote Git URL.'.format(
                    repository=repository
                )
            )

        if len(remotes) == 1:
            return remotes[0]

        for remote in remotes:
            if remote.name == _GIT_DEFAULT_REMOTE_NAME:
                return remote

        return remotes[0]

    def _get_git_push_url(directory):
        repository = base.Repo(directory)
        remote = _get_preferred_remote(repository)
        push_url = repository.git.config(
            "--get", "remote.{remote.name}.url".format(remote=remote)
        )

        if push_url:
            return push_url

        raise RuntimeError(
            'Directory "{directory}" found no push URL.'.format(directory=directory)
        )

    def _get_repository_url(package):
        directory = finder.get_package_root(package)

        return _get_git_push_url(directory)

    if item is not None:
        raise ValueError("Item is not set as deferred.")

    return _get_repository_url


def _validate_directory(directory):
    """Ensure ``directory`` is a folder on-disk.

    Args:
        directory (str): The absolute path to a folder which must exist on-disk.

    Raises:
        ValueError: If ``directory`` is some completely unknown type.
        RuntimeError: If ``directory`` doesn't exist on-disk.

    """
    if not isinstance(directory, six.string_types):
        raise ValueError(
            'Item "{directory}" is not a string.'.format(directory=directory)
        )

    if os.path.isdir(directory):
        return directory

    raise RuntimeError(
        'Directory "{directory}" does not exist.'.format(directory=directory)
    )


def _validate_github_access_token(item):
    """Check if ``item`` is a raw GitHub personal access token string.

    Args:
        item (str): Example: ``"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"``.

    Raises:
        ValueError: If ``item`` is not a string.
        RuntimeError: If ``item`` does not match GitHub's personal access token format.

    """
    if not isinstance(item, six.string_types):
        raise ValueError('Item "{item}" is not a string.'.format(item=item))

    if _GITHUB_PERSONAL_ACCESS_TOKEN.match(item):
        return

    raise RuntimeError(
        'Text "{item}" is not a known GitHub access token.'.format(item=item)
    )


def _validate_json_file(item):
    """Convert a file path at ``item`` from JSON to a Python object.

    Args:
        item (str): The absolute or relative path to a JSON file on-disk.

    Raises:
        ValueError: If ``item`` isn't a readable JSON file.

    Returns:
        object: The found JSON content. Usually, it's a :obj:`dict`.

    """
    if not isinstance(item, six.string_types):
        raise ValueError('Item "{item!r}" is not a path.'.format(item=item))

    if not os.path.isfile(item):
        raise ValueError('Path "{item}" does not exist on-disk'.format(item=item))

    with io.open(item, "r", encoding="utf-8") as handler:
        return json.load(handler)


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


def _validate_publish_string(item):
    """Check if ``item`` is a standard string.

    If ``item`` is empty, it's assumed that the user wants to publish **every**
    version of a package, without omission.

    Args:
        item (str): The object to check.

    Raises:
        ValueError: If ``item`` isn't a string

    Returns:
        _sre.SRE_Pattern or str: The converted ``item``.

    """
    if not isinstance(item, six.string_types):
        raise ValueError('Item "{item!r}" is not a string.'.format(item=item))

    if not item:
        # TODO : Need a unittest to ensure this works
        return re.compile(".+")  # Allow any version, even if it isn't SemVer

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


def _validate_ssh(item):
    """Check if ``item`` is a SSH-style git URL.

    Args:
        item (str): A website or similar URI. Like "git@github.com/foo/bar".

    Raises:
        ValueError: If ``item`` isn't a URL / URI.

    Returns:
        dict[str, str]: The original, unaltered ``item``, and its captured text.

    """
    match = _SSH_EXPRESSION.match(item)

    if match:
        output = match.groupdict()
        output[ORIGINAL_TEXT] = item

        return output

    raise ValueError(
        'Item "{item}" is invalid. It must match "{_SSH_EXPRESSION.pattern}".'.format(
            item=item, _SSH_EXPRESSION=_SSH_EXPRESSION
        )
    )


def _validate_url(item):
    """Check if ``item`` is a URL / URI.

    Args:
        item (str): A website or similar URI. Like "http://www.foo.bar".

    Raises:
        ValueError: If ``item`` isn't a URL / URI.

    Returns:
        dict[str, str]: The original, unaltered ``item``, and its captured text.

    """
    result = urllib_parse.urlparse(item)

    if all((result.scheme, result.netloc)):
        parts = result.path.split(_URL_SUBDIRECTORY_SEPARATOR)

        return {GROUP: parts[1], ORIGINAL_TEXT: item, REPOSITORY: parts[2]}

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


def _validate_view_url(item):
    """Check if ``item`` is a website URL or a directory.

    Either is considered a "valid" documentation view location. Because either
    are viewable in a website browser.

    Args:
        item (str):
            A website or similar URI. Like "http://www.foo.bar" or an inner folder to check.

    Raises:
        ValueError: If ``item`` isn't a sub-directory.

    """
    if os.path.isdir(item):
        # If it's actually a directory on-disk, just use it as-is
        return item

    _validate_url(item)

    return item


NON_EMPTY_STR = schema.Use(_validate_non_empty_str)

DEFAULT_PUBLISH_PATTERN = "{package.version.major}.{package.version.minor}"
PUBLISH_PATTERNS = schema.Or(_validate_regex, _validate_publish_string)

CALLABLE = schema.Use(_validate_callable)

DIRECTORY = schema.Use(_validate_directory)
URL = schema.Use(_validate_url)
URL_SUBDIRECTORY = schema.Use(_validate_url_subdirectory)
SSH = schema.Use(_validate_ssh)
DEFER_REPOSITORY = schema.Use(_validate_defer_git_repository)

JSON_FILE_PATH = schema.Use(_validate_json_file)

GITHUB_ACCESS_TOKEN = schema.Use(_validate_github_access_token)

VIEW_URL = schema.Use(_validate_view_url)
