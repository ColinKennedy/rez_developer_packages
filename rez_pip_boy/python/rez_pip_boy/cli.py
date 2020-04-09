#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import os
import shlex
import tempfile

from rez import pip
from rez.cli import pip as cli_pip
from rez_utilities import inspection

from .core import builder, exceptions, filer


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
        destination_package = installed_variant.install(arguments.destination)
        root = inspection.get_package_root(installed_variant)
        filer.transfer(installed_variant)
        builder.add_build_command(destination_package)
