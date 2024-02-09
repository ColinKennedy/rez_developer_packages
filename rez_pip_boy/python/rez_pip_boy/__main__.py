#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The entry point of ``rez_pip_boy``. Run this module to execute the CLI."""

from __future__ import print_function

import logging
import sys

from . import cli
from .core import exceptions


def main():
    """Run the main execution of the current script."""
    try:
        cli.main(sys.argv[1:])
    except exceptions.ExceptionBase as error:
        print(
            "{error.__class__.__name__}: {error}".format(error=error),
            file=sys.stderr,
        )

        sys.exit(error.code)


if __name__ == "__main__":
    _LOGGER = logging.getLogger("rez_pip_boy")
    _HANDLER = logging.StreamHandler(sys.stdout)
    _HANDLER.setLevel(logging.INFO)
    _FORMATTER = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    _HANDLER.setFormatter(_FORMATTER)
    _HANDLER.setLevel(logging.DEBUG)
    _LOGGER.addHandler(_HANDLER)

    main()
