#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function

import sys

from .core import exceptions
from . import cli


def main():
    """Run the main execution of the current script."""
    try:
        cli.main(sys.argv)
    except (exceptions.MissingTests, exceptions.NoValidPackageFound) as error:
        print(str(error), file=sys.stderr)


if __name__ == "__main__":
    main()
