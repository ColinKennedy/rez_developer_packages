#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""A module that's devoted to building and "creating" Rez packages."""

import copy
import logging
import os

from rez import build_process_, build_system, packages_
from rez.cli import build as build_
from rez.cli import release as release_
from rez.config import config

from . import rez_configuration

_LOGGER = logging.getLogger(__name__)


def build(package, install_path, packages_path=None):
    """Build the given Rez `package` to the given `install_path`.

    Args:
        package (:class:`rez.developer_package.DeveloperPackage`):
            The package to build.
        install_path (str):
            The absolute directory on-disk to build the package at.
            This path represents a path that you might add to the
            REZ_PACKAGES_PATH environment variable (for example) so it
            should not contain the package's name or version.
        packages_path (list[str], optional):
            The paths that will be used to search for Rez packages while
            building. This is usually to make it easier to find package
            dependencies. If `packages_path` is not defined, Rez will
            use its default paths. Default is None.

    Raises:
        RuntimeError: If the package fails to build for any reason.

    Returns:
        :class:`rez.developer_package.DeveloperPackage`:
            The package the represents the newly-built package.

    """
    if packages_path:
        # If the user has custom paths to use for building, prefer those
        # Reference: https://github.com/nerdvegas/rez/blob/da16fdeb754ccd93c8ce54fa2b6a4d4ef3601e6b/src/rez/build_process_.py#L232 pylint: disable=line-too-long
        #
        package = copy.deepcopy(package)
        package.config.packages_path[:] = packages_path

    directory = os.path.dirname(package.filepath)

    system = build_system.create_build_system(directory, package=package, verbose=True)

    builder = build_process_.create_build_process(
        "local",  # See :func:`rez.build_process_.get_build_process_types` for possible values
        directory,
        build_system=system,
        verbose=True,
    )

    _LOGGER.info('Now building package "%s".', package)

    with rez_configuration.get_context():
        number_of_variants_visited = builder.build(
            clean=True, install=True, install_path=install_path
        )

    if not number_of_variants_visited:
        raise RuntimeError(
            'Building "{package}" failed. No variants were installed.'.format(
                package=package
            )
        )

    if not os.listdir(install_path):
        raise RuntimeError(
            'Package "{package}" has an installed variant '
            "but no files were written to-disk.".format(package=package)
        )

    return packages_.get_developer_package(
        os.path.join(install_path, package.name, str(package.version))
    )


def release(directory, options, parser, new_release_path, search_paths=None):
    """Release a package located at `directory` to the `new_release_path` folder.

    Args:
        directory (str):
            A directory that is cd'ed into just before the release
            command is run. This directory must have a valid package.py,
            package.txt, or package.yaml inside of it.
        options (:class:`argparse.Namespace`):
            The parsed, user-provided options that `parser` generated.
        parser (:class:`argparse.ArgumentParser`):
            The main object that actually forces Rez to create the
            unleash. It's also used for piping errors and other
            features. But this function doesn't make particular use of
            any of those.
        new_release_path (str):
            The directory where the newly created and released Rez
            package will go. If no directory is given then a default
            path is created and used. Default: "".
        search_paths (list[str], optional):
            The directories on-disk that can be used to help find extra
            dependencies that a Rez package might require. Default is None.

    Raises:
        ValueError: If `directory` is not a folder on-disk.

    Returns:
        str:
            The directory where the released package was sent to.
            Normally, this should always be `new_release_path`. But
            if `new_release_path` wasn't given then this returns a
            temporary directory.

    """

    def _clear_rez_get_current_developer_package_cache():
        # Reference: https://github.com/nerdvegas/rez/blob/master/src/rez/cli/build.py#L9-L29
        build_._package = None  # pylint: disable=protected-access

    if not os.path.isdir(directory):
        raise ValueError(
            'Directory "{directory}" does not exist.'.format(directory=directory)
        )

    if not search_paths:
        search_paths = []

    current_directory = os.getcwd()
    release_path = config.release_packages_path
    packages_path = list(config.packages_path)  # pylint: disable=no-member
    _clear_rez_get_current_developer_package_cache()

    try:
        # The paths changed here serve 2 purposes
        #
        # 1. release_packages_path gets changed so that the released
        #    package goes to `new_release_path` and not to the regular
        #    release path.
        # 2. packages_path needs to be given the release path + any
        #    other paths needed to resolve the package (e.g. folders were
        #    dependencies may live.
        #
        config.release_packages_path = new_release_path
        config.packages_path[:] = [  # pylint: disable=no-member
            new_release_path
        ] + search_paths
        os.chdir(directory)

        release_.command(options, parser)
    except Exception:
        raise
    finally:
        config.release_packages_path = release_path
        config.packages_path[:] = packages_path  # pylint: disable=no-member
        os.chdir(current_directory)

    return new_release_path
