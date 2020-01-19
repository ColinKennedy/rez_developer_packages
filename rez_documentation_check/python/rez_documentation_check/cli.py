#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The main module that checks for Rez package issues."""

import collections
import fnmatch
import logging
import os

from python_compatibility.sphinx import conf_manager
from rez import packages_
from rez_utilities import url_help

from .core import exceptions, sphinx_helper

_LOGGER = logging.getLogger(__name__)


def _is_conf_file_missing(directory):
    """bool: Check if a Sphinx conf.py can be found starting at `directory` Rez package."""
    return not conf_manager.get_conf_file(directory)


def get_existing_intersphinx_links(directory):
    """Find the intersphinx information that's already written on-disk.

    Args:
        directory (str):
            The root directory of the Rez package. It's assumed that
            this directory has documentation written for it.

    Raises:
        EnvironmentError:
            If a conf.py was found but its ``intersphinx_mapping`` attribute is invalid.

    Returns:
        dict[str, tuple[str, NoneType]]:
            Each intersphinx label and the URL + target location.

    """
    conf_file = conf_manager.get_conf_file(directory)

    if not conf_file:
        _LOGGER.debug(
            'Directory "%s" has no Sphinx conf.py file was found. '
            "Returning an empty dict.",
            directory,
        )
        return dict()

    module = conf_manager.import_conf_file(conf_file)

    if hasattr(module, "intersphinx_mapping"):
        mapping = module.intersphinx_mapping or dict()

        if not isinstance(mapping, collections.MutableMapping):
            raise EnvironmentError(
                'conf.py "{conf_file}" has an intersphinx_mapping but it is not a dict.'.format(
                    conf_file=conf_file
                )
            )

        return mapping

    return dict()


def get_missing_intersphinx_mappings(
    package, sphinx_files_must_exist=False
):
    """Find every intersphinx key / URL that exists as a Python import but is not written to-disk.

    Args:
        package (:class:`rez.developer_package.DeveloperPackage`):
            The Rez package to use for finding existing intersphinx mapping data.
        sphinx_files_must_exist (bool, optional):
            If True and the "conf.py" files doesn't exist, raise an
            If exception. False and the file doesn't exist, don't error
            If and just keep moving. Default is False.

    Raises:
        :class:`.exceptions.SphinxFileMissing`:
            If the Sphinx conf.py is missing and `sphinx_files_must_exist` is True.

    Returns:
        dict[str, str]: The dependency Rez package + its API documentation URL.

    """
    root = os.path.dirname(package.filepath)

    # TODO : Check if `sphinx_files_must_exist` is still in-use
    if sphinx_files_must_exist and _is_conf_file_missing(root):
        raise exceptions.SphinxFileMissing(
            "conf.py is missing. Either set sphinx_files_must_exist to False "
            "or create a conf.py to continue."
        )

    links = find_intersphinx_links(package.requires or [])
    existing = get_existing_intersphinx_links(root)
    existing.update(links)

    return existing


def find_intersphinx_links(requirements):
    """Convert a Rez package's list of requirements into API documentation links.

    Args:
        requirements (iter[:class:`rez.utils.formatting.PackageRequest`]):
            The Package + version (if there is a version) information
            that will be used to query documentation details.

    Returns:
        dict[str, tuple[str, None]]:
            Get every Rez package and its URL help documentation, if found.

    """
    packages = set()

    for requirement in requirements:
        package = packages_.get_latest_package(
            requirement.name, range_=requirement.range_
        )

        if package:
            packages.add(package)

            continue

        _LOGGER.warning('No Rez package was found for requirement "%s".', requirement)

    output = dict()

    finders = [url_help.find_package_documentation, url_help.find_api_documentation]

    for package in packages:
        for finder in finders:
            documentation = finder(package)

            if documentation:
                output[package.name] = (documentation, None)

                break

    return output


def fix_intersphinx_mapping(  # pylint: disable=too-many-arguments
    package, sphinx_files_must_exist, excluded_packages
):
    """Replace or add the ``intersphinx_mapping`` attribute to a user's conf.py Sphinx file.

    Args:
        package (:class:`rez.developer_package.DeveloperPackage`):
            The Rez package to modify with a new, updated intersphinx mapping.
        sphinx_files_must_exist (bool, optional):
            If True and the "conf.py" files doesn't exist, raise an
            exception. If False and the file doesn't exist, don't error
            If and just keep moving. Default is False.
        excluded_packages (iter[str]):
            The names of Rez packages to ignore. Any intersphinx
            key/value pair that matches any of the names given to this
            parameter will be ignored. This parameter supports glob matching.

    Raises:
        :class:`.exceptions.SphinxFileMissing`:
            If `sphinx_files_must_exist` but the source package has no
            documentation.

    Returns:
        bool: If False, no fix was applied. If True, at least one file on-disk was changed.

    """
    root = os.path.dirname(package.filepath)

    if sphinx_files_must_exist and _is_conf_file_missing(root):
        raise exceptions.SphinxFileMissing(
            "conf.py is missing. Either set sphinx_files_must_exist to False "
            "or create a conf.py to continue."
        )

    try:
        missing = get_missing_intersphinx_mappings(
            package, sphinx_files_must_exist=False
        )
    except exceptions.SphinxFileMissing:
        raise exceptions.SphinxFileMissing(
            'Package "{package.name}" has no conf.py file. '
            "Please create it and re-run this command.".format(package=package)
        )

    missing = {
        name: item
        for name, item in missing.items()
        if not any(fnmatch.fnmatch(name, pattern) for pattern in excluded_packages)
    }

    if not missing:
        return False

    conf_file = conf_manager.get_conf_file(root)
    links = get_existing_intersphinx_links(root)
    links.update(missing)

    sphinx_helper.replace_intersphinx_mapping(links, conf_file)

    return True
