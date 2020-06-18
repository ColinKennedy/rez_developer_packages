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
    except (exceptions.MissingDoubleDash, exceptions.SwappedArguments) as error:
        print(error, file=sys.stderr)
        print(
            'The left side of "{cli.ARGUMENTS_SEPARATOR}" is for `rez-pip` arguments. The right is for `rez_pip_boy` arguements.'.format(cli=cli),
            file=sys.stderr,
        )

        sys.exit(exceptions.MISSING_DOUBLE_DASH_EXIT_CODE)
    except exceptions.MissingDestination as error:
        print(error, file=sys.stderr)
        print('Only use one "{cli.ARGUMENTS_SEPARATOR}", please.'.format(cli=cli))

        sys.exit(exceptions.MISSING_DESTINATION_FOLDER_EXIT_CODE)
    except exceptions.DuplicateDoubleDash as error:
        print(error, file=sys.stderr)
        print('Only use one "{cli.ARGUMENTS_SEPARATOR}", please.'.format(cli=cli))

        sys.exit(exceptions.DUPLICATE_DOUBLE_DASH_EXIT_CODE)


if __name__ == "__main__":
    logging.basicConfig(stream=sys.stdout, level=logging.WARNING)
    __LOGGER = logging.getLogger(__name__)
    __HANDLER = logging.StreamHandler(stream=sys.stdout)
    __FORMATTER = logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")
    __HANDLER.setFormatter(__FORMATTER)
    __LOGGER.addHandler(__HANDLER)

    main()
