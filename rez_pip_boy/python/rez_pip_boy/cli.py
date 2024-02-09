#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The main parser module which creates Rez pip packages."""

import argparse
import atexit
import contextlib
import functools
import logging
import os
import shutil
import tempfile

from rez import pip
from rez.cli import pip as cli_pip
from rez_utilities import rez_configuration

from .core import _build_command, builder, exceptions, filer, hashed_variant, pather

_LOGGER = logging.getLogger(__name__)
_SUCCESS_EXIT_CODE = 0
_NOT_SET = object()


def _parse_arguments(text):
    """Get the ``rez-pip`` command arguments + the directory where installed files should go.

    Args:
        text (list[str]): User-provided arguments, split by spaces.

    Raises:
        Exception: If `text` is invalid input.

    Returns:
        tuple[str, :class:`argparse.Namespace`]:
            The raw text to parse with `rez-pip` and the parsed arguments
            needed by `rez_pip_boy`.

    """
    parser = argparse.ArgumentParser(
        description="A thin wrapper around ``rez-pip`` to transform an installed package "
        "back into a source package.",
    )

    description = "All commands of this CLI."
    subparsers = parser.add_subparsers(help=description, description=description)

    description = 'Download from pip and "install" the pseudo-source package.'
    installer = subparsers.add_parser(
        "install",
        help=description,
        description=description,
    )

    description = "Build a --no-dependencies pseudo-source into an installed package."
    source_builder = subparsers.add_parser(
        "build-from-source",
        help=description,
        description=description,
    )

    _add_installer_arguments(installer)
    _add_build_from_source_arguments(source_builder)
    _add_verbose_argument(installer)
    _add_verbose_argument(source_builder)

    return parser.parse_args(text)


def _is_older_rez(arguments):
    """bool: Check if the ``rez-pip`` parsed arguments represent an older Rez version (2.47-ish)."""
    try:
        arguments.extra
    except AttributeError:  # pragma: no cover
        return True

    return False


def _get_install_context(arguments):
    """Create a Python context object for running the main shell command.

    This context will help us implement Rez package installs which use
    hashed variants as well as un-hashed variants.

    Args:
        arguments (:class:`argparse.ArgumentParser`): The user-parsed arguments.

    Returns:
        callable: Some callable Python object which is later used as a Python context.

    """
    if arguments.hashed_variants:
        return hashed_variant.do_nothing

    return hashed_variant.force_unhashed_variants


@contextlib.contextmanager
def _get_verbosity_context(_):
    """Get a Python context used for controlling printed text.

    Args:
        quiet (bool):
            If True, return a context that will prevent print-out to the
            user's terminal. If False, print everything as normal, instead.

    Returns:
        The found Python context.

    """
    with hashed_variant.do_nothing():
        yield
    # Note: Handle this somehow, on Windows
    # if not quiet:
    #     with hashed_variant.do_nothing():
    #         yield
    # else:
    #     with wurlitzer.pipes() as (stdout, stderr):
    #         yield
    #
    #     stdout.close()
    #     stderr.close()


def _add_build_from_source_arguments(parser):
    parser.add_argument(
        "--build-directory",
        help="A temporary location to assemble the extracted files.",
    )

    parser.add_argument(
        "--install-directory",
        help="The final folder where all unpacked files and folders will go.",
    )

    parser.set_defaults(execute=_build_from_source)


def _add_installer_arguments(parser):
    """Add all of the options for ``rez_pip_boy install``.

    Args:
        parser (argparser.ArgumentParser): The location where the arguments will go.

    """
    parser.add_argument(
        "request",
        help=(
            "The package request to download with pip and install. "
            'e.g. "six", "six==1.14.0", "six-1+<2", etc.'
        ),
    )

    parser.add_argument(
        "--install-directory",
        required=True,
        help=(
            "The package request to download with pip and install. "
            'e.g. "six", "six==1.14.0", "six-1+<2", etc.'
        ),
    )

    parser.add_argument(
        "--tar-directory",
        default=_NOT_SET,
        help=(
            "The directory on-disk to place tar files. "
            "By default this goes to $PIP_BOY_TAR_LOCATION"
        ),
    )

    parser.add_argument(
        "--python-version",
        required=True,
        help="The major.minor version to install to. e.g. 3.9.",
    )

    parser.add_argument(
        "--hashed-variants",
        action="store_true",
        help="Install Rez packages using a hashed variant folder names.",
    )

    parser.add_argument(
        "--no-make-folders",
        action="store_true",
        help="When included, folders will not be automatically created for you. "
        "If a folder doesn't exist, the script exits.",
    )

    parser.add_argument(
        "--keep-temporary-files",
        action="store_true",
        help=(
            "When included, no files will be automatically cleaned up. "
            "You'll be responsible for deleting them."
        ),
    )

    parser.add_argument(
        "--no-dependencies",
        action="store_true",
        help=(
            "By default, rez_pip_boy is an inserted dependency to all builds. "
            "Adding this flag inlines rez_pip_boy so there's no dependency. "
        ),
    )

    parser.add_argument(
        "-q",
        "--quiet",
        action="store_true",
        help="When enabled rez-pip won't print anything to the terminal.",
    )

    parser.set_defaults(execute=_install)


def _add_verbose_argument(parser):
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="If included, debug logs are shown.",
    )


def _build_from_source(arguments):
    """Run the ``build-from-source`` sub-parser.

    This is usually called from a pseudo-source Rez package, during ``rez-build --ci``.

    Args:
        arguments (argparse.Namespace): The parsed user arguments to build / install from.

    """
    build_directory = arguments.build_directory or os.environ["REZ_BUILD_PATH"]
    install_directory = (
        arguments.install_directory or os.environ["REZ_BUILD_INSTALL_PATH"]
    )

    _build_command.main(build_directory, install_directory)


def _install(arguments):
    """Download and install a pip package, using ``arguments``.

    Args:
        arguments (argparse.Namespace): The parsed user data to query from.

    Raises:
        MissingDestination: If the given directory doesn't exist.

    """
    _validate_tar_location(arguments)
    destination = os.path.expanduser(os.path.expandvars(arguments.install_directory))

    if not os.path.isdir(destination):
        if arguments.no_make_folders:
            raise exceptions.MissingDestination(
                'Path "{destination}" is not a directory. Please create it and try again.'
                "".format(destination=destination)
            )

        os.makedirs(destination)

    prefix = pather.normalize(
        tempfile.mkdtemp(prefix="rez_pip_boy_", suffix="_temporary_build_folder")
    )

    if not arguments.keep_temporary_files:
        atexit.register(functools.partial(shutil.rmtree, prefix))

    rez_pip_command = [
        "--install",
        arguments.request,
        "--python-version",
        arguments.python_version,
    ]

    _LOGGER.debug('Found "%s" rez-pip arguments.', rez_pip_command)

    rez_pip_arguments = _parse_rez_pip_arguments(rez_pip_command)

    context = _get_install_context(arguments)

    with _get_verbosity_context(not arguments.verbose), context():
        installed_variants = _pip_install(rez_pip_arguments, prefix)

    _LOGGER.debug('Found variants "%s".', installed_variants)

    for installed_variant in installed_variants:
        _LOGGER.info(
            'Now installing variant "%s" to "%s" folder.',
            installed_variant,
            destination,
        )
        variant = installed_variant.install(destination, dry_run=True)

        if variant:
            _LOGGER.info('Variant "%s" is already installed. Skipping.', variant)

            continue

        if arguments.no_dependencies:
            overrides = builder.get_no_dependencies_overrides()
        else:
            overrides = builder.get_normal_dependencies_overrides()

        destination_package = installed_variant.install(
            destination,
            overrides=overrides,
        )
        filer.transfer(arguments.tar_directory, installed_variant)

        if arguments.no_dependencies:
            builder.add_build_file(destination_package)


def _parse_rez_pip_arguments(text):
    """Process `text` as if it was sent to the `rez-pip` command and send the data back.

    Args:
        text (list[str]):
            User-provided arguments, split by spaces. These values
            should be whatever you'd normally pass to rez-pip.
            e.g. "--install black --python-version=3.7"

    Returns:
        :class:`argparse.Namespace`: All of the parsed arguments from `text`.

    """
    temporary_parser = argparse.ArgumentParser(
        description="A temporary parser to communicate with rez-pip's API.",
    )

    cli_pip.setup_parser(temporary_parser)

    return temporary_parser.parse_args(text)


def _pip_install(arguments, prefix):
    """Install the given ``rez-pip`` arguments to the ``prefix`` folder.

    Args:
        arguments (:class:`argparse.Namespace`):
            The arguments coming from ``rez-pip``'s parser. Not the
            parsed arguments from ``rez_pip_boy``.
        prefix (str):
            An absolute path to a directory on-disk. This location is
            where the packages will be installed to.

    Returns:
        tuple[:class:`rez.packages.Variant`, str, str]:
            The installed variants and any print messages and error
            messages which were found during installation.

    """
    if not _is_older_rez(arguments):
        (
            installed_variants,
            _,
        ) = pip.pip_install_package(  # pylint: disable=unexpected-keyword-arg
            arguments.PACKAGE,
            pip_version=arguments.pip_ver,
            python_version=arguments.py_ver,
            release=arguments.release,
            prefix=prefix,
            extra_args=arguments.extra,
        )
    else:
        # Older Rez versions don't have the `prefix` or `extra_args` parameters
        # So we need to do more to get it to work.
        #
        with rez_configuration.patch_local_packages_path(prefix):
            installed_variants, _ = pip.pip_install_package(
                arguments.PACKAGE,
                pip_version=arguments.pip_ver,
                python_version=arguments.py_ver,
                release=False,
            )

    return installed_variants


def _validate_tar_location(arguments):
    """Make sure ``--tar-directory`` was set or we have a fallback directory to use.

    Args:
        arguments (argparse.Namespace): The ``install`` sub-parser arguments.

    Raises:
        MissingTarLocation: If no tar directory was set.
        BadTarLocation: If a tar directory is found but it doesn't exist on-disk.

    """
    directory = arguments.tar_directory

    if directory == _NOT_SET:
        if "PIP_BOY_TAR_LOCATION" not in os.environ:
            raise exceptions.MissingTarLocation(
                "No --tar-directory was given and $PIP_BOY_TAR_LOCATION is missing."
            )

        directory = os.environ["PIP_BOY_TAR_LOCATION"]

    if not os.path.isdir(directory):
        raise exceptions.BadTarLocation(
            'Path "{directory}" is not a directory on-disk. '
            "Please check spelling and try again.".format(directory=directory)
        )

    arguments.tar_directory = directory


def main(text):
    """Install the user's requested Python package as source Rez packages.

    Args:
        text (list[str]):
            User-provided arguments, split by spaces. These values
            should be whatever you'd normally pass to rez-pip as well as
            the folder where they'd like to put the generated packages.
            e.g. '"--install black --python-version=3.7" --destination /tmp/foo'.

    """
    arguments = _parse_arguments(text)

    if arguments.verbose:
        package_logger = logging.getLogger("rez_pip_boy")
        package_logger.setLevel(logging.DEBUG)

    _LOGGER.debug('Arguments "%s" found.', arguments)
    _LOGGER.debug('Will execute "%s" function.', arguments.execute)

    arguments.execute(arguments)
