"""The main module that implements the :ref:`rez_build_helper` CLI."""

import argparse
import logging
import os
import typing

from . import argparse_action, filer, linker, namespacer

_LOGGER = logging.getLogger(__name__)


class _Arguments(typing.NamedTuple):
    """The parsed user input."""

    eggs: list[str]
    hdas: list[str]
    items: list[str]
    shared_python_packages: list[namespacer.PythonPackageItem]
    symlink: bool
    symlink_files: bool
    symlink_folders: bool
    verbose: bool


def _parse_arguments(text: list[str]) -> _Arguments:
    """Create arguments for building file(s)/folder(s) of a Rez package.

    Args:
        text:
            The user-provided text from command-line. This is usually
            space-separated text.

    Returns:
        The parsed user-provided text.

    """
    parser = argparse.ArgumentParser(
        description="Build Python-based Rez packages in just a single command.",
    )

    parser.add_argument(
        "--hdas",
        action=argparse_action.Path,
        nargs="+",
        help="The relative paths to each folder containing VCS-style Houdini HDAs.",
    )

    parser.add_argument(
        "--items",
        nargs="+",
        help="The relative paths to each file/folder to copy / install.",
    )

    parser.add_argument(
        "--shared-python-packages",
        action=argparse_action.NamespacePathPair,
        nargs="+",
        help="Each namespace + relative paths for a shared Python namespace + package. "
        "e.g. prefix.namespace:python{separator}".format(separator=os.pathsep),
    )

    parser.add_argument(
        "--eggs",
        action=argparse_action.Path,
        nargs="+",
        help="The relative paths to each file/folder to make into a .egg file.",
    )

    parser.add_argument(
        "--symlink",
        action="store_true",
        default=linker.must_symlink(),
        help="If True, symlink everything back to the source Rez package.",
    )

    parser.add_argument(
        "--symlink-files",
        action="store_true",
        default=linker.must_symlink_files(),
        help="If True, symlink files back to the source Rez package.",
    )

    parser.add_argument(
        "--symlink-folders",
        action="store_true",
        default=linker.must_symlink_folders(),
        help="If True, symlink folders back to the source Rez package.",
    )

    parser.add_argument(
        "--verbose", action="store_true", help="If included, more logs will be shown."
    )

    known, _ = parser.parse_known_args(text)

    return typing.cast(_Arguments, known)


def main(text: list[str]) -> None:
    """Parse the user input and run the :ref:`rez_build_helper` terminal command.

    Args:
        text: Unparsed user input to use.

    """
    arguments = _parse_arguments(text)

    if arguments.verbose:
        logger = logging.getLogger("rez_build_helper")
        level = logging.DEBUG
        logger.setLevel(level)

        for handler in logger.handlers:
            handler.setLevel(level)

    source = os.environ["REZ_BUILD_SOURCE_PATH"]
    destination = os.environ["REZ_BUILD_INSTALL_PATH"]

    _LOGGER.debug('Build Source: "%s" directory.', source)
    _LOGGER.debug('Build Install: "%s" directory.', destination)

    filer.clean(destination)

    filer.build(
        source,
        destination,
        hdas=arguments.hdas,
        items=arguments.items,
        eggs=arguments.eggs,
        shared_python_packages=arguments.shared_python_packages,
        symlink=arguments.symlink,
        symlink_folders=arguments.symlink_folders,
        symlink_files=arguments.symlink_files,
    )
