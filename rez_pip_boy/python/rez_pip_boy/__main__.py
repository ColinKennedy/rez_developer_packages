#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The entry point of ``rez_pip_boy``. Run this module to execute the CLI."""

import logging
import sys

from . import cli


def main():
    """Run the main execution of the current script."""
    cli.main(sys.argv[1:])


if __name__ == "__main__":
    logging.basicConfig(stream=sys.stdout, level=logging.WARNING)
    __LOGGER = logging.getLogger(__name__)
    __HANDLER = logging.StreamHandler(stream=sys.stdout)
    __FORMATTER = logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")
    __HANDLER.setFormatter(__FORMATTER)
    __LOGGER.addHandler(__HANDLER)

    main()
