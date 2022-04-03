"""Automatically add :ref:`rez_sphinx tags <rez_sphinx tag>` to built packages."""

import logging
import functools
import io
import os
import re

from rez_utilities import finder

from . import preprocess_entry_point
from ..core import configuration, constant, environment, sphinx_helper
from ..preferences import preference, preference_init


_HAS_CURLIES = re.compile("{[^{}]*}")
_LOGGER = logging.getLogger(__name__)
_ROOT_FORMAT = "{root}"


def _has_unresolved_help(help_):
    """Check if ``help_`` has some {} string that needs expanding.

    Note:
        I feel like I've solved this problem before in a much more effective
        way, using :class:`string.Formatter`. Can't remember it though, oh
        well.

    Args:
        help_ (list[list[str, str]]): The help text to consider.

    Returns:
        bool: If there's at least one {} to expand, return True.

    """
    for _, destination in help_:
        if _HAS_CURLIES.search(destination):
            return True

    return False


def _find_help_labels(root):
    """Auto-find all `package help`_ links, using :ref:`rez_sphinx`.

    It works by querying all Sphinx .rst files at ``root`` (or whatever your
    source extension is), checks each file to a known :ref:`rez_sphinx tag`,
    and then adds those entries directly into the users's `package help`_
    just before it is built.

    Args:
        root (str):
            The root documentation source directory. It should directly contain
            a `Sphinx conf.py`_.

    Returns:
        list[list[str, str]]:
            Each found label + destination entry, if any. If no destination is
            defined, a destination is auto-assigned directly to the
            documentation file.

    """
    tags = []

    # TODO : Consider making this a non-hard-coded value
    extension = ".html"

    for path in _iter_sphinx_source_files(root):
        fallback_name = os.path.splitext(os.path.relpath(path, root))[0]
        fallback_destination = fallback_name + extension

        for label, destination in _get_rez_sphinx_tags(path):
            if not destination:
                destination = fallback_destination
            else:
                destination = sphinx_helper.htmlize_ref(
                    fallback_destination, destination
                )

            entry = [label, os.path.join(constant.ROOT_REPLACEMENT, destination)]

            if entry not in tags:
                tags.append(entry)

    return tags


def _get_rez_sphinx_tags(path):
    """Grab all tags within ``path``.

    Args:
        path (str): The Sphinx ReST file to load and directly parse.

    Returns:
        list[list[str, str]]: Each hard-coded label + "destination", if any.

    """
    with io.open(path, "r", encoding="utf-8") as handler:
        data = handler.read()

    return preference_init.find_tags(data.split("\n"))


def _iter_sphinx_source_files(root):
    """Find every Sphinx ReST file within ``root``.

    Args:
        root (str):
            The root documentation source directory. It should directly contain
            a `Sphinx conf.py`_.

    Yields:
        str: The absolute path to every Sphinx ReST file, if any.

    """
    sphinx = configuration.ConfPy.from_directory(root)
    extension = sphinx.get_source_extension()

    for current_root, _, files in os.walk(root):
        for name in files:
            if name.endswith(extension):
                yield os.path.join(current_root, name)


def _sort(sort_method, original_help, full_help):
    """Sort ``full_help`` based on the other parameters.

    Args:
        sort_method (callable[list[list[str, str]], str]):
            A function that takes ``original_help`` plus some sort term
            to determine where the sort term should be placed.
        original_help (list[list[str, str]]):
            The user's original `package help`_ data, if any.
        full_help (iter[list[str, str]]):
            The user's original `package help`_ data, plus any auto-found
            data, if any.

    Returns:
        list[list[str, str]]: The final, sorted `package help`_.

    """
    sorter = functools.partial(sort_method, original_help)

    return sorted(full_help, key=sorter)


def _resolve_format_text(help_, package):
    """Convert all ``{root}`` format strings in ``help_`` to a publish location.

    Args:
        help_ (list[list[str, str]]):
            The documentation which may contain format strings like
            ``[["Home Page", "{root}/path.html"]]``.
        package (rez.packages.Package):
            The object to query from, for configuration settings.

    Returns:
        list[list[str, str]]: The original list, but with all format strings resolved.

    """
    output = []

    url = environment.get_publish_url(package)

    for key, value in help_:
        resolved = value.format(
            root=url,  # This we expect to probably exist.
            package=package,  # This is added, just in case.
        )
        output.append([key, resolved])

    return output


def preprocess_help(package_source_root, help_):  # pylint: disable=unused-argument
    """Get auto-generated `help` attributes for a Rez source package.

    If the source Rez package at ``package_source_root`` has no `Sphinx
    conf.py`_, this function returns nothing.

    Args:
        package_source_root (str):
            An absolute path to a directory on disk where some source Rez package lives.
        help_ (list[str] or str or NoneType):
            The found Rez package help, if any.

    Returns:
        list[list[str, str]]: The original ``help_`` plus any auto-generated help entries.

    """
    help_ = preprocess_entry_point.expand_help(help_)

    try:
        source_path = sphinx_helper.find_configuration_path(package_source_root)
    except RuntimeError:
        _LOGGER.debug('Package at "%s" has no documentation.', package_source_root)

        return []

    if not source_path:
        return []

    source_root = os.path.dirname(source_path)
    new_labels = _find_help_labels(source_root)

    # TODO : Make sure we incorporate user preference here. e.g. if no all
    # duplicates, only add if we prefer auto-generated.
    #
    new_labels.append([constant.REZ_SPHINX_OBJECTS_INV, constant.ROOT_REPLACEMENT])

    original_help = help_
    sort_method = preference.get_sort_method()

    try:
        filter_method = preference.get_filter_method()
    except EnvironmentError:
        full_help = help_ + new_labels
        full_help = _sort(sort_method, original_help, full_help)
    else:
        filtered_original, filtered_labels = filter_method(original_help, new_labels)
        full_help = _sort(
            sort_method, filtered_original, filtered_original + filtered_labels
        )

    if _has_unresolved_help(full_help) and environment.is_publishing_enabled():
        package = finder.get_nearest_rez_package(package_source_root)
        full_help = _resolve_format_text(full_help, package)

    return full_help
