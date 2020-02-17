"""The entry point for the ``rez_move_imports`` CLI."""

from __future__ import print_function

import sys

from .core import exception
from . import cli

if __name__ == "__main__":
    known_exceptions = (
        exception.InvalidDirectory,
        exception.InvalidInput,
        exception.MissingDirectory,
        exception.MissingNamespaces,
    )

    try:
        cli.main(sys.argv[1:])
    except known_exceptions as error:
        print(str(error), file=sys.stderr)
        sys.exit(exception.MissingNamespaces.error_code)
