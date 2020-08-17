#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse

from rez import packages

from .core import environment, exceptions


def _parse_arguments(text):
    parser = argparse.ArgumentParser(description="")

    parser.add_argument("package_request", help="The Rez package to make an environment for.")
    parser.add_argument("tests", nargs="+", required=True, help="The test requirements to append to the package request.")

    return parser.parse_args(text)


def main(text):
    arguments = _parse_arguments(text)
    package = packages.get_latest(arguments.package_request)

    if not package:
        raise exceptions.NoValidPackageFound('Request "{arguments.package_request}" doesn\'t match a Rez package.'.format(arguments=arguments))

    environment.run(package, arguments.tests)
