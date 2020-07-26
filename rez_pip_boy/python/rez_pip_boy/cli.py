#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The main parser module which creates Rez pip packages."""

import argparse
import atexit
import functools
import logging
import os
import shlex
import shutil
import tempfile

import wurlitzer
from rez import pip
from rez.cli import pip as cli_pip
from rez_utilities import rez_configuration

from .core import builder, exceptions, filer, hashed_variant

ARGUMENTS_SEPARATOR = " -- "
_BUILD_FILE_NAME = "rezbuild.py"
_LOGGER = logging.getLogger(__name__)


def _parse_arguments(text):
    """Get the ``rez-pip`` command arguments + the directory where installed files should go.

    Args:
        text (list[str]): User-provided arguments, split by spaces.

    Raises:
        Exception: If `text` is invalid input.

    Returns:
        tuple[str, :class:`argparse.Namespace`]:
            The raw text to parse with `rez-pip` and the parsed arguments needed by `rez_pip_boy`.

    """
    separator = ARGUMENTS_SEPARATOR.strip()

    if text.count(separator) > 1:
        raise exceptions.DuplicateDoubleDash(
            "Please provide only one {ARGUMENTS_SEPARATOR!r}.".format(
                ARGUMENTS_SEPARATOR=ARGUMENTS_SEPARATOR,
            ),
        )

    try:
        index = text.index(separator)
    except ValueError:
        raise exceptions.MissingDoubleDash(
            "You must separate your arguments with {ARGUMENTS_SEPARATOR!r}.".format(
                ARGUMENTS_SEPARATOR=ARGUMENTS_SEPARATOR
            )
        )

    rez_pip_arguments = text[:index]
    rez_pip_command = " ".join(rez_pip_arguments)
    rez_pip_boy_arguments = text[index + 1 :]  # Add `+ 1` to remove the "--" separator

    parser = argparse.ArgumentParser(
        description="A thin wrapper around ``rez-pip`` to transform an installed package "
        "back into a source package.",
    )

    parser.add_argument(
        "destination",
        help="The absolute folder path on-disk to place this source package "
        "(usually a sub-folder in a git repository).",
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
        help="When included, no files will be automatically cleaned up. "
        "You'll be responsible for deleting them.",
    )

    parser.add_argument(
        "-q",
        "--quiet",
        action="store_true",
        help="When enabled rez-pip won't print anything to the terminal.",
    )

    try:
        arguments = parser.parse_args(rez_pip_boy_arguments)
    except SystemExit:
        parser.parse_args(rez_pip_arguments)

        raise exceptions.SwappedArguments(
            "Your arguments are separated by {ARGUMENTS_SEPARATOR!r} but they need to be flipped.".format(  # pylint: disable=line-too-long
                ARGUMENTS_SEPARATOR=ARGUMENTS_SEPARATOR,
            ),
        )

    return rez_pip_command, arguments


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


def _get_verbosity_context(quiet):
    """Get a Python context used for controlling printed text.

    Args:
        quiet (bool):
            If True, return a context that will prevent print-out to the
            user's terminal. If False, print everything as normal, instead.

    Returns:
        The found Python context.

    """
    if not quiet:
        return hashed_variant.do_nothing()

    return wurlitzer.pipes()


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


def main(text):
    """Install the user's requested Python package as source Rez packages.

    Args:
        text (list[str]):
            User-provided arguments, split by spaces. These values
            should be whatever you'd normally pass to rez-pip as well as
            the folder where they'd like to put the generated packages.
            e.g. '"--install black --python-version=3.7" --destination /tmp/foo'.

    Raises:
        :class:`.MissingDestination`: If the given directory doesn't exist.

    """
    rez_pip_command, rez_pip_boy_arguments = _parse_arguments(text)
    destination = os.path.expanduser(
        os.path.expandvars(rez_pip_boy_arguments.destination)
    )

    if not os.path.isdir(destination):
        if rez_pip_boy_arguments.no_make_folders:
            raise exceptions.MissingDestination(
                'Path "{destination}" is not a directory. Please create it and try again.'
                "".format(destination=destination)
            )

        os.makedirs(destination)

    prefix = tempfile.mkdtemp(prefix="rez_pip_boy_", suffix="_temporary_build_folder")

    if not rez_pip_boy_arguments.keep_temporary_files:
        atexit.register(functools.partial(shutil.rmtree, prefix))

    rez_pip_arguments = _parse_rez_pip_arguments(shlex.split(rez_pip_command))

    context = _get_install_context(rez_pip_boy_arguments)

    with _get_verbosity_context(rez_pip_boy_arguments.quiet):
        with context():
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

        build_command = "python {{root}}/{_BUILD_FILE_NAME}".format(
            _BUILD_FILE_NAME=_BUILD_FILE_NAME
        )
        destination_package = installed_variant.install(
            destination, overrides={"build_command": build_command},
        )
        filer.transfer(installed_variant)
        builder.add_build_file(destination_package, _BUILD_FILE_NAME)
