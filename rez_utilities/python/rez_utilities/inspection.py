#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Generic rez-specific functions.

This module has several functions that refer to "built", "released",
or "installed" Rez packages. Structurally, these are all the same Rez
package. But they may contain different data in the package.py. For
example, only a released Rez package has version-control information
added to it. Built packages doesn't have a package.py in them but
released and installed package do.

The term "source" Rez package just means "A Rez package that's in a
repository and isn't built, released, or installed.

All installed and released Rez packages are "built" Rez packages.
All "source" Rez packages are by definition not "built".

"""

import logging
import os
import tempfile

from python_compatibility import filer, imports
from rez import exceptions, packages_, resolved_context
from rez.config import config

from . import creator

_LOGGER = logging.getLogger(__name__)


def _is_path_variant_and_has_python_package(root, path, variants):
    """Check if a path is inside of a source Rez package's list of variants.

    This function's purpose is hard to describe.
    :func:`has_python_package` is meant to work with source
    Rez packages or built Rez packages. But the problem with
    supporting source Rez packages is that a source Rez package
    may contain 1+ variants. This causes problems because a path
    like "/some/repository/my_rez_package/python-2.7/python" (where
    "/some/repository/my_rez_package" is the Rez package `root` and
    "/some/repository/my_rez_package/python" is the real folder path)
    doesn't exist on-disk until the Rez package is built.

    But most Python Rez packages have a Python variant. So that'd mean
    :func:`has_python_package` would have to build every Rez package it
    encounters just to find out if it has a Python module inside of it.
    Yikes, right?

    This function exists to reasonably guess if the "source Rez package
    which contains 1+ variants" actually does have a Python package
    inside of it without needing to build it.

    Note:
        If the package has no variants, this function must always return False.

    Args:
        root (str):
            The directory that contains the Rez package's package.py,
            package.txt, or package.yaml.
        path (str):
            A path that may be a sub-folder inside of the Rez package.
        variants (iter[list[:class:`rez.utils.formatting.PackageRequest`]]):
            A Rez package's different build configurations. Usually,
            this will just be different Python versions such as
            [[PackageRequest("python-2.7")]] but it can be more complex.

    Returns:
        bool: If `path` is a file variant file path inside of a Rez package.

    """
    for variant_less_path in iter_variant_extracted_paths(root, path, variants):
        if not imports.has_importable_module(
            variant_less_path, ignore={"__init__.py"}
        ):
            # This condition happens only when a Rez package defines
            # A Python package but the package is empty. Which
            # probably is user error and shouldn't happen often.
            #
            _LOGGER.warning(
                'Path "%s" is inside "%s" but no Python module could be found.',
                path,
                root,
            )

            continue

        return True

    return False


def is_built_package(package):
    """Check if the given Rez package is a source directory or a built Rez package.

    Note:
        A "built" package is a package that was created using
        "rez-build", "rez-release" or similar.

    Args:
        package (:class:`rez.packages_.Package`): The Rez package to check.

    Raises:
        ValueError: If the object given to `package` is an invalid input.

    Returns:
        bool: If the packge is built.

    """
    try:
        parent_folder = get_package_root(package)
    except (AttributeError, TypeError):
        raise ValueError(
            'Input "{package}" is not a valid Rez package.'.format(package=package)
        )

    return str(package.version) == os.path.basename(parent_folder)


# TODO : Check if there's a better way to do this function.
# Maybe there's a way to query the package's editted variables via resources?
#
def has_python_package(package, paths=None, allow_build=True):
    """Check if the given Rez package has at least one Python package inside of it.

    Note:
        This function assumes that `package` is a built package.
        Otherwise, it may return incorrect results.

    Important:
        This function assumes that all Python packages set / append to
        the PYTHONPATH environment variable. It uses that environment variable
        to find Python packages.

    Args:
        package (:class:`rez.packages_.Package`):
            The Rez package to check for Python packages.
        paths (list[str], optional):
            The locations on-disk that will be used to any
            Rez-environment-related work. Some plugins need these paths
            for resolving a context, for example. If no paths are given,
            :attr:`rez.config.config.packages_path` is used instead.
            Default is None.
        allow_build (bool, optional):
            If `package` is a source Rez package and no importable
            Python modules could be found and this parameter is True,
            build the package to see if its generated content includes
            a Python module. If False though, this function will simply
            return False without building the Rez source package.
            Default is True.

    Raises:
        ValueError: If `package` is not a Rez package.

    Returns:
        bool: If a Python package is detected.

    """
    if not hasattr(package, "name") or not hasattr(package, "version"):
        raise ValueError(
            'Object "{package}" is not a valid Rez package.'.format(package=package)
        )

    if not paths:
        paths = config.packages_path  # pylint: disable=no-member

    version = ""
    is_built = is_built_package(package)

    if is_built:
        version = package.version

    context = resolved_context.ResolvedContext(
        ["{package.name}=={version}".format(package=package, version=version)],
        package_paths=[get_packages_path_from_package(package)] + paths,
    )

    environment = context.get_environ()
    root = get_package_root(package)
    paths = environment.get("PYTHONPATH", "").split(os.pathsep)

    if not paths:
        return False

    for path in paths:
        if filer.in_directory(path, root, follow=False) or filer.in_directory(
            path, root, follow=True
        ):
            # This condition occurs in 1 of 2 scenarios
            # 1. The Rez package is built
            # 2. The Rez package is a source package but contains no variants
            #
            if imports.has_importable_module(path, ignore={"__init__.py"}):
                return True

        if not is_built:
            if _is_path_variant_and_has_python_package(
                root, path, package.variants or []
            ):
                return True

    if is_built or not allow_build:
        return False

    # If the package is a source package and PYTHONPATH is defined but
    # no path was found, it may actually be that the Python files are
    # generated on-build (such as C++ files with Python bindings). To
    # find out, we need to run this function again, but with the built
    # package.
    #
    build_directory = tempfile.mkdtemp()
    build_package = creator.build(package, build_directory)

    return has_python_package(build_package)


def get_nearest_rez_package(directory):
    """Assuming that `directory` is on or inside a Rez package, find the nearest Rez package.

    Args:
        directory (str):
            The absolute path to a folder on disk. This folder should be
            a sub-folder inside of a Rez package to the root of the Rez package.

    Returns:
        :class:`rez.developer_package.DeveloperPackage` or NoneType: The found package.

    """
    previous = None
    original = directory

    if not os.path.isdir(directory):
        directory = os.path.dirname(directory)

    while directory and previous != directory:
        previous = directory

        try:
            return packages_.get_developer_package(directory)
        except exceptions.PackageMetadataError:
            pass

        directory = os.path.dirname(directory)

    _LOGGER.debug(
        'Directory "%s" is either inaccessible or is not part of a Rez package.',
        original,
    )

    return None


def get_packages_path_from_package(package):
    """Get the folder above a Rez package, assuming the path is to a built Rez package.

    The "packages path" of a Rez package is basically "The path
    that would be needed in order to make this package discoverable
    by the rez-env command". For example, a released package like
    "~/.rez/packages/int/foo/1.0.0" has a packages path like
    "~/.rez/packages/int" but if the package is not built and is just
    a source package like "~/repositories/my_packages/foo" then the
    packages path is "~/repositories/my_packages".

    Args:
        package (:class:`rez.packages_.Package`):
            The built, installed, or source Rez package to get a valid path from.

    Returns:
        str: The found parent directory.

    """
    root = get_package_root(package)

    if is_built_package(package):
        package_name_folder = os.path.dirname(root)

        return os.path.dirname(package_name_folder)

    return os.path.dirname(root)


def get_package_root(package):
    """Find the directory that contains the gizen Rez package.

    Depending on if the Rez package is a regular package or a developer
    package, the logic is slightly different.

    Args:
        package (:class:`rez.packages_.Package`):
            The built or source Rez package to get a valid path from.

    Raises:
        EnvironmentError:
            If the found Rez package does not have a root folder. This
            exception should only happen if the Rez package is damaged
            somehow.

    Returns:
        str: The found folder. A Rez package should always have a root folder.

    """
    path_to_package = package.resource.location

    if not os.path.isdir(path_to_package) and hasattr(package, "filepath"):
        return os.path.dirname(package.filepath)

    path = os.path.join(path_to_package, package.name, str(package.version))

    if not os.path.isdir(path):
        raise EnvironmentError(
            'Package "{package}" has an invalid path "{path}".'
            "".format(package=package, path=path)
        )

    return path


def get_root_key(name):
    """Get the environment variable that shows where a Rez package lives on-disk.

    Args:
        name (str): The name of the Rez package.

    Returns:
        str: The environment variable for the Rez package.

    """
    return "REZ_{name}_ROOT".format(name=name.upper())


def iter_latest_packages(paths=None, packages=None):
    """Get one package from every Rez package family.

    Args:
        paths (list[str], optional):
            The directories to search for Rez package families,
            Default: :attr:`rez.config.config.packages_path`.
        packages (set[str], optional):
            If this parameter is given a value, any Rez package families
            that are discovered in `paths` will be filtered by the list
            of Rez package family names in this parameter.

    Yields:
        :class:`rez.packages_.Package`:
            The latest version of every package in the current environment.

    """
    names = sorted(
        set(family.name for family in packages_.iter_package_families(paths=paths))
    )

    if packages:
        names = [name for name in names if name in packages]

    for name in names:
        package = packages_.get_latest_package(name, paths=paths)

        if not package:
            _LOGGER.warning(
                'Package family "%s" was found but `get_latest_package` returned None.'
                "The package is probably damaged.",
                name,
            )

            continue

        yield package


def iter_variant_extracted_paths(root, path, variants):
    """Convert a Rez package path that contains a variant back into its "non-variant" form.

    Args:
        root (str):
            The directory that contains the Rez package's package.py,
            package.txt, or package.yaml.
        path (str):
            A path that is a sub-folder inside of the Rez package. This
            path also has a variant somewhere in it.
        variants (iter[list[:class:`rez.utils.formatting.PackageRequest`]]):
            A Rez package's different build configurations. Usually,
            this will just be different Python versions such as
            [[PackageRequest("python-2.7")]] but it can be more complex.

    Yields:
        str: The original `path` but without a variant.

    """
    for variant in variants:
        inner_path = os.path.join(*[str(request) for request in variant])
        resolved_path = os.path.join(root, inner_path)

        if filer.in_directory(path, resolved_path, follow=False):
            yield path.replace(inner_path + os.sep, "")
