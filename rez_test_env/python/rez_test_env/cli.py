#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse

from .core import environment


def _parse_arguments(text):
    parser = argparse.ArgumentParser(description="")

    parser.add_argument("package_request", help="The Rez package to make an environment for.")
    parser.add_argument("tests", nargs="+", help="The test requirements to append to the package request.")

    return parser.parse_args(text)


def main(text):
    arguments = _parse_arguments(text)
    environment.run(arguments.package_request, arguments.tests)
