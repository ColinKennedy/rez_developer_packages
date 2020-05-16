#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import logging
import sys

from .core import installer


__LOGGER = logging.getLogger("rez_yum_installer")
__HANDLER = logging.StreamHandler(stream=sys.stdout)
__FORMATTER = logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")
__LOGGER.setLevel(logging.INFO)
__HANDLER.setFormatter(__FORMATTER)
__LOGGER.addHandler(__HANDLER)


def _add_arguments(parser):
    subparsers = parser.add_subparsers(title="The commands used by rez_yum_installer.")
    install = subparsers.add_parser("install")
    install.add_argument("name", help='The name of the Yum package to install (e.g. "xdotool").')
    install.set_defaults(execute=_install)

    parser.add_argument("-v", "--verbose", action="store_true", help="Print more log messages.")


def _install(arguments):
    installer.install(arguments.name)


def main(text):
    """Run the main execution of the current script."""
    parser = argparse.ArgumentParser(description="Install any Yum package as a Rez package.")
    _add_arguments(parser)
    arguments = parser.parse_args(text)

    if arguments.verbose:
        __LOGGER.setLevel(logging.DEBUG)

    arguments.execute(arguments)


if __name__ == "__main__":
    main(sys.argv[1:])
