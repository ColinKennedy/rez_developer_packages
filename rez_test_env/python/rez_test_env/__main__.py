#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The main entry-point for the `rez_test_env` CLI.

This file gets called directly by the user.

"""

from __future__ import print_function

import sys

from .core import exceptions
from . import cli


def main():
    """Run the main execution of the current script."""
    try:
        cli.main(sys.argv[1:])
    except (exceptions.MissingTests, exceptions.NoValidPackageFound) as error:
        print(str(error), file=sys.stderr)


if __name__ == "__main__":
    main()
