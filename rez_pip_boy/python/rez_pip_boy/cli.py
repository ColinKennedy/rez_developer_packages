#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import os
import shlex
import tempfile

from rez import pip
from rez.cli import pip as cli_pip
from rez_utilities import inspection

from .core import exceptions, filer


def _parse_arguments(text):
    parser = argparse.ArgumentParser(
        description="A thin wrapper around ``rez-pip`` to transform an installed package back into a source package.",
    )

    parser.add_argument(
        "command",
        help='The raw rez-pip command. e.g. "--install black --python-version=3.6".',
    )

    parser.add_argument(
        "destination",
        help="The absolute folder path on-disk to place this source package (usually a sub-folder in a git repository).",
    )

    parser.add_argument(
        "--tar-location",
        default=os.getenv("REZ_PIP_BOY_TAR_LOCATION", ""),
        help="The directory on-disk to place the compressed, variant data that each install creates.",
    )

    return parser.parse_args(text)


def _parse_rez_pip_arguments(text):
    """Process `text` as if it was sent to the `rez-pip` command and send the data back.

    Returns:
        :class:`argparse.Namespace`: All of the parsed arguments from `text`.

    """
    temporary_parser = argparse.ArgumentParser(
        description="A temporary parser to communicate with rez-pip's API.",
    )

    cli_pip.setup_parser(temporary_parser)

    return temporary_parser.parse_args(text)


# TODO : Remove?
def _prepare_install_path(tokens, path):
    def _get_index(tokens):
        try:
            return tokens.index("-p")
        except ValueError:
            pass

        try:
            return tokens.index("-prefix")
        except ValueError:
            pass

        return -1

    output = []

    index = _get_index(output)

    if index != -1:
        raise ValueError(
            'Tokens "{tokens}" contains -p/--prefix. Please remove it.'.format(tokens=tokens)
        )

    output.extend(tokens)
    output.extend(["--prefix", path])

    return output


def _get_common_folder(paths):
    prefix = os.path.commonprefix(paths)

    # `prefix` isn't guaranteed to be an actual folder so we must split the end off
    return prefix.rpartition(os.path.sep)[0]


def _get_common_variant_folder(root):
    # """Find the folder which marks the start of an installed variant.
    #
    # Args:
    #     root (str): The directory of some Rez package to """
    paths = {
        os.path.join(root_, name)
        for root_, _, files in os.walk(root)
        for name in files
    }

    try:
        paths.remove(os.path.join(root, "package.py"))
    except KeyError:
        pass

    try:
        paths.remove(os.path.join(root, "package.yaml"))
    except KeyError:
        pass

    return _get_common_folder(paths)


def main(text):
    arguments = _parse_arguments(text)

    if not os.path.isdir(arguments.destination):
        raise exceptions.MissingDestination(
            'Path "{arguments.destination}" is not a directory. Please create it and try again.'
            ''.format(arguments=arguments)
        )

    prefix = tempfile.mkdtemp(prefix="rez_pip_boy_", suffix="_temporary_build_folder")

    # TODO : Remove --prefix from `parser`
    # TODO : Make sur that temporary files are cleaned up on-exit
    rez_pip_arguments = _parse_rez_pip_arguments(shlex.split(arguments.command))

    installed_variants, _ = pip.pip_install_package(
        rez_pip_arguments.PACKAGE,
        pip_version=rez_pip_arguments.pip_ver,
        python_version=rez_pip_arguments.py_ver,
        release=rez_pip_arguments.release,
        prefix=prefix,
        extra_args=rez_pip_arguments.extra)

    for installed_variant in installed_variants:
        installed_variant.install(arguments.destination)
        root = inspection.get_package_root(installed_variant)
        variant_root = os.path.join(root, installed_variant._non_shortlinked_subpath)
        filer.transfer(variant_root, arguments.destination)
