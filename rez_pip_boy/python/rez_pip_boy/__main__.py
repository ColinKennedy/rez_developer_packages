#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The entry point of ``rez_pip_boy``. Run this module to execute the CLI."""

import sys

from . import cli


def main():
    """Run the main execution of the current script."""
    cli.main(sys.argv[1:])


if __name__ == "__main__":
    main()
