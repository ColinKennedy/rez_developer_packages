#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The main module that checks for Rez package issues."""

import collections
import fnmatch
import itertools
import logging
import os

from python_compatibility.sphinx import conf_manager
from rez_utilities import inspection

from .core import exceptions, python_dependency, sphinx_helper

_LOGGER = logging.getLogger(__name__)


def _is_conf_file_missing(directory):
    """bool: Check if a Sphinx conf.py can be found starting at `directory` Rez package."""
    return not conf_manager.get_conf_file(directory)


def _get_package_root_from_environment(package):
    """Find the directory where the Rez package lives on-disk.

    Important:
        This function assumes that the user is currently in a resolved
        context which includes `package`.

    Note:
        :meth:`rez.developer_package.DeveloperPackage.filepath` only
        shows you the root of the Rez package. It doesn't get the
        package's variant path. This function will always return the
        correct variant folder path.

    Args:
        package (:class:`rez.developer_package.DeveloperPackage`):
            The Rez package to find the root directory of.

    Returns:
        str:
            The found directory root. If `package` is not in the user's
            current resolved context, return nothing, instead.

    """
    return os.getenv(inspection.get_root_key(package.name), "")


def _check_for_packages(package_groups):
    """Find if any package is missing.

    Args:
        package_groups (
            iter[tuple[:class:`rez.developer_package.DeveloperPackage`] or NoneType,
            set[str]]
        ):
            Each Rez package and the directories located inside of it.

    Raises:
        EnvironmentError:
            If any of the given items ing `package_groups` are invalid packages.

    """
    invalids = set()

    for package, directories in package_groups:
        if not package:
            invalids.update(directories)

    if invalids:
        raise EnvironmentError(
            "These groups of directories are not actually "
            'inside of a Rez package. "{invalids}". Cannot continue.'.format(
                invalids=sorted(invalids)
            )
        )


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
    package,
    items,
    sphinx_files_must_exist=False,
    add_rez_requirements=False,
    allow_non_api=False,
):
    """Find every intersphinx key / URL that exists as a Python import but is not written to-disk.

    Args:
        package (:class:`rez.developer_package.DeveloperPackage`):
            The Rez package to use for finding existing intersphinx mapping data.
        items (set[str]):
            The absolute file(s)/folder(s) on-disk to Python files which
            will be used to search for additional intersphinx data.
        sphinx_files_must_exist (bool, optional):
            If True and the "conf.py" files doesn't exist, raise an
            If exception. False and the file doesn't exist, don't error
            If and just keep moving. Default is False.
        add_rez_requirements (bool, optional):
            If False, only Python imported modules will be used to
            search for documentation. If True, this function will also
            include all Rez packages in a user's ``requires`` attribute
            for documentation. Default is False.
        allow_non_api (bool, optional):
            If False, only "recognized" API documentation will be
            returned. If True, all types of Rez documentation will be
            searched. Basically, False "guesses" correct documentation.
            Default is False.

    Raises:
        :class:`.exceptions.SphinxFileMissing`:
            If the Sphinx conf.py is missing and `sphinx_files_must_exist` is True.

    Returns:
        dict[str, str]: The dependency Rez package + its API documentation URL.

    """
    root = os.path.dirname(package.filepath)

    if sphinx_files_must_exist and _is_conf_file_missing(root):
        raise exceptions.SphinxFileMissing(
            "conf.py is missing. Either set sphinx_files_must_exist to False "
            "or create a conf.py to continue."
        )

    links = find_intersphinx_links(
        items, add_rez_requirements=add_rez_requirements, allow_non_api=allow_non_api
    )
    existing = get_existing_intersphinx_links(root)
    existing.update(links[package.name])

    return existing


def find_intersphinx_links(items, add_rez_requirements=False, allow_non_api=False):
    """Check a collection of Python files / folders for a recommended intersphinx mapping.

    The intersphinx mapping is based on Python modules that are imported
    by every Python file found in `items`.

    Args:
        items (iter[str]):
            The absolute paths to Python files or folders (of Python files).
        add_rez_requirements (bool, optional):
            If False, only Python imported modules will be used to
            search for documentation. If True, this function will also
            include all Rez packages in a user's ``requires`` attribute
            for documentation. Default is False.
        allow_non_api (bool, optional):
            If False, only "recognized" API documentation will be
            returned. If True, all types of Rez documentation will be
            searched. Basically, False "guesses" correct documentation.
            Default is False.

    Returns:
        list[tuple[:class:`rez.developer_package.DeveloperPackage`, dict[str, tuple[str, None]]]]:
            Each Rez package and its list of Rez package dependencies
            + the URL to that package dependency's API documentation.
            dependencies will only be returned if API documentation can
            be found for them.

    """
    package_groups = itertools.groupby(
        sorted(set(items)), key=inspection.get_nearest_rez_package
    )
    package_groups = [
        (package, list(directories)) for package, directories in package_groups
    ]

    _check_for_packages(package_groups)

    output = dict()

    for package, directories in package_groups:
        root = _get_package_root_from_environment(package)
        _LOGGER.debug(
            'Found package "%s" and root "%s" (root may be empty and that\'s okay).',
            package,
            root,
        )

        if root:
            # This section happens if the user has `package` sourced in
            # their current environment.
            #
            links = python_dependency.get_intersphinx_links_using_current_environment(
                package.name, directories
            )
            links.update(
                python_dependency.get_intersphinx_links_from_requirements(
                    package.requires or [], allow_non_api=allow_non_api
                )
            )
        else:
            # This section attempts to resolve `package` and then read
            # its requirements, directly.
            #
            _LOGGER.info(
                'The user\'s current environment does not contain package "%s".',
                package.name,
            )
            _LOGGER.info(
                "A new environment will be resolved to find the recommended intersphinx mapping."
            )
            links = python_dependency.get_intersphinx_links_from_rez_environment(
                package,
                directories,
                add_rez_requirements=add_rez_requirements,
                allow_non_api=allow_non_api,
            )

        if links:
            output[package.name] = links

    return output


def fix_intersphinx_mapping(  # pylint: disable=too-many-arguments
    package,
    items,
    sphinx_files_must_exist,
    excluded_packages,
    add_rez_requirements,
    allow_non_api=False,
):
    """Replace or add the ``intersphinx_mapping`` attribute to a user's conf.py Sphinx file.

    Args:
        package (:class:`rez.developer_package.DeveloperPackage`):
            The Rez package to modify with a new, updated intersphinx mapping.
        items (set[str]):
            The absolute file(s)/folder(s) to Python files which
            will be used to search for additional intersphinx data.
        sphinx_files_must_exist (bool, optional):
            If True and the "conf.py" files doesn't exist, raise an
            exception. If False and the file doesn't exist, don't error
            If and just keep moving. Default is False.
        excluded_packages (iter[str]):
            The names of Rez packages to ignore. Any intersphinx
            key/value pair that matches any of the names given to this
            parameter will be ignored. This parameter supports glob matching.
        add_rez_requirements (bool):
            If False, only Python imported modules will be used to
            search for documentation. If True, this function will also
            include all Rez packages in a user's ``requires`` attribute
            for documentation. Default is False.
        allow_non_api (bool, optional):
            If False, only "recognized" API documentation will be
            returned. If True, all types of Rez documentation will be
            searched. Basically, False "guesses" correct documentation.
            Default is False.

    Raises:
        :class:`.exceptions.SphinxFileMissing`:
            If `sphinx_files_must_exist` but the source package has no
            documentation.

    """
    root = os.path.dirname(package.filepath)

    if sphinx_files_must_exist and _is_conf_file_missing(root):
        raise exceptions.SphinxFileMissing(
            "conf.py is missing. Either set sphinx_files_must_exist to False "
            "or create a conf.py to continue."
        )

    try:
        missing = get_missing_intersphinx_mappings(
            package,
            items,
            sphinx_files_must_exist=False,
            add_rez_requirements=add_rez_requirements,
            allow_non_api=allow_non_api,
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
