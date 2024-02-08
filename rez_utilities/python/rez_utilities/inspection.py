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

import atexit
import functools
import logging
import os
import shutil
import tempfile

from python_compatibility import filer, imports
from rez import packages_, resolved_context
from rez.config import config

from . import finder

_LOGGER = logging.getLogger(__name__)


def _get_variant_less_path(root, path, variants):
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
    for variant_less_path in _iter_variant_extracted_paths(root, path, variants):
        if not imports.has_importable_module(variant_less_path, ignore={"__init__.py"}):
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


def _iter_variant_extracted_paths(root, path, variants):
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
    for variant in sorted(variants, key=len, reverse=True):
        inner_path = os.path.join(*[str(request) for request in variant])
        resolved_path = os.path.join(root, inner_path)

        if filer.in_directory(path, resolved_path, follow=False):
            yield path.replace(inner_path + os.sep, "")


def in_valid_context(package):
    """Find out if the user can query dependencies without creating another context.

    Args:
        package (:class:`rez.packages_.Package`): Some package to check.

    Returns:
        bool:
            If False, it means that we need to create a context
            from scratch if we want to query the dependencies
            of the given `package`. If True, it means that just
            calling from :mod:`subprocess` should work.

    """
    return os.getenv("REZ_{name}_VERSION".format(name=package.name.upper())) == str(
        package.version
    )


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
        parent_folder = finder.get_package_root(package)
    except (AttributeError, TypeError):
        raise ValueError(
            'Input "{package}" is not a valid Rez package.'.format(package=package)
        )

    version = str(package.version)

    if not version:
        return False

    return version == os.path.basename(parent_folder)


def has_python_package(  # pylint: disable=too-many-branches,too-many-locals,too-complex
    package, paths=None, allow_build=True, allow_current_context=False
):
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
        allow_current_context (bool, optional):
            If ``True``, use this current environment's ``$PYTHONPATH``. If
            ``False``, create a brand new Rez context and get its resolved
            ``$PYTHONPATH`` instead.

    Raises:
        ValueError: If `package` is not a Rez package.

    Returns:
        bool: If a Python package is detected.

    """
    # Avoiding a cyclic import
    from . import creator  # pylint: disable=import-outside-toplevel

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

    if allow_current_context and in_valid_context(package):
        environment = os.environ.get("PYTHONPATH", "").split(os.pathsep)
    else:
        context = resolved_context.ResolvedContext(
            ["{package.name}=={version}".format(package=package, version=version)],
            package_paths=[get_packages_path_from_package(package)] + paths,
        )

        environment = context.get_environ().get("PYTHONPATH", "").split(os.pathsep)

    python_files = get_package_python_paths(package, environment)

    # All zipped .egg files as valid Python "packages"
    for path in python_files:
        if path.endswith(".egg") and os.path.isfile(path):
            return True

    for root_path in python_files:
        for _, _, files in os.walk(root_path):
            for file_path in files:
                if file_path == "__init__.py":
                    continue

                if file_path.endswith(".py"):
                    return True

    if is_built or not allow_build:
        return False

    # If the package is a source package and PYTHONPATH is defined but
    # no path was found, it may actually be that the Python files are
    # generated on-build (such as C++ files with Python bindings). To
    # find out, we need to run this function again, but with the built
    # package.
    #
    build_directory = tempfile.mkdtemp(suffix="_some_temporary_rez_build_package")
    build_package = creator.build(package, build_directory, quiet=True)

    # Reference: https://stackoverflow.com/questions/3850261/doing-something-before-program-exit
    atexit.register(functools.partial(shutil.rmtree, build_directory))

    return has_python_package(build_package)


def get_package_python_paths(package, paths):
    """Get the Python files that a Rez package adds to the user's PYTHONPATH.

    If the Rez package is an installed Rez package and it contains
    variants, each variant will have its paths returned.

    Note:
        This function is a bit sub-optimal. Basically, Rez's API should
        have a way to just query an individual package's contribution
        to PYTHONPATH. But currently doesn't. So we have to hack around
        the problem by using a Rez context.

    Reference:
        https://github.com/nerdvegas/rez/issues/737
        https://github.com/nerdvegas/rez/pull/739
        https://rez-talk.slack.com/archives/CHELFCTFB/p1578604659006100

    Args:
        package (:class:`rez.packages_.Package`):
            The built or source Rez package to get a valid path from.
        paths (iter[str]):
            The PYTHONPATH paths within the Rez package.

    Returns:
        set[str]: The found Python files (excluding __init__.py files).

    """
    # Note: Here we're trying to get `package`'s specific changes to PYTHONPATH (if any)
    #
    # Unfortunately, the Rez API doesn't really support this yet.
    # There's 2 GitHub links that may one-day implement it though:
    #     - https://github.com/nerdvegas/rez/issues/737
    #     - https://github.com/nerdvegas/rez/pull/739
    #
    # Reference: https://rez-talk.slack.com/archives/CHELFCTFB/p1578604659006100
    #
    # Once that work is merged, replace `get_package_python_paths` with it.
    #
    root = os.path.normcase(os.path.realpath(finder.get_package_root(package)))

    if is_built_package(package):
        return {path for path in paths if filer.in_directory(path, root, follow=False)}

    output = set()

    for path in paths:
        # If the Rez package is a source Rez package + has variants
        # we need to strip the "variants" out of `path`, before
        # returning it.
        #
        try:
            variant_less_path = next(
                _iter_variant_extracted_paths(root, path, package.variants or [])
            )
        except StopIteration:
            pass
        else:
            output.add(variant_less_path)

            continue

        if filer.in_directory(path, root, follow=False) or filer.in_directory(
            path, root, follow=True
        ):
            output.add(path)

            continue

    return output


def get_all_packages(directory):
    """Find every Rez package in the given directory.

    Args:
        directory (str):
            An absolute path to a folder on-disk. y package on or below
            this path will be returned.

    Returns:
        list[:class:`rez.packages_.DeveloperPackage`]: The found packages.

    """
    paths = set()
    packages = []

    for root, _, _ in os.walk(directory):
        if any(filer.in_directory(root, directory_) for directory_ in paths):
            continue

        package = finder.get_nearest_rez_package(root)

        if package:
            packages.append(package)

    return packages


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
    root = finder.get_package_root(package)

    if is_built_package(package):
        package_name_folder = os.path.dirname(root)

        return os.path.dirname(package_name_folder)

    return os.path.dirname(root)


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
