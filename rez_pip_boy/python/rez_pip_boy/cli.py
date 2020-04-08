#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import os
import shlex
import sys
import tempfile

from rez import pip
from rez.cli import pip as cli_pip
from rez import packages_
from rez import package_maker
from rez_utilities import inspection

from .core import exceptions


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
    temporary_parser = argparse.ArgumentParser(
        description="A temporary parser to communicate with rez-pip's API.",
    )

    cli_pip.setup_parser(temporary_parser)

    return temporary_parser.parse_args(text)


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


def _graft_package(variant, path):
    package_ = variant.parent
    # We must not try to copy "config" from the Rez package. If we do, Rez raises a SchemaError
    allowed_keys = package_.keys - {"config"}

    with package_maker.make_package(variant.name, path) as pkg:
        for attribute in allowed_keys:
            value = getattr(variant, attribute)
            setattr(pkg, attribute, value)


def _copy_data(variant, path):
    pass
    # raise NotImplementedError('Need to write')


def main(text):
    arguments = _parse_arguments(text)

    if not os.path.isdir(arguments.destination):
        raise exceptions.MissingDestination(
            'Path "{arguments.destination}" is not a directory. Please create it and try again.'
            ''.format(arguments=arguments)
        )

    prefix = tempfile.mkdtemp(prefix="rez_pip_boy_", suffix="_temporary_build_folder")

    # TODO : Remove --prefix from `parser`
    rez_pip_arguments = _parse_rez_pip_arguments(shlex.split(arguments.command))

    installed_variants, _ = pip.pip_install_package(
        rez_pip_arguments.PACKAGE,
        pip_version=rez_pip_arguments.pip_ver,
        python_version=rez_pip_arguments.py_ver,
        release=rez_pip_arguments.release,
        prefix=prefix,
        extra_args=rez_pip_arguments.extra)

    for installed_variant in installed_variants:
        _graft_package(installed_variant, arguments.destination)
        _copy_data(installed_variant, arguments.destination)
