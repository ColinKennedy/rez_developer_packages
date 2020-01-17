#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import shlex
import sys

from . import cli
from .core import check_exception


def _parse_arguments(text):
    parser = argparse.ArgumentParser(
        description="A CI linter that checks if API documentation needs to be re-generated.",
    )

    parser.add_argument(
        "command",
        help="The exact ``sphinx-apidoc`` call that will be used to write API documentation.",
    )

    return parser.parse_args(text)


def main(text):
    """Run the main execution of the current script."""
    arguments = _parse_arguments(text)

    try:
        cli.check(shlex.split(arguments.command))
    except check_exception.CoreException as error:
        sys.exit(str(error))


if __name__ == "__main__":
    main(sys.argv[1:])
