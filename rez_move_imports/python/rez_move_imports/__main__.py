"""The entry point for the ``rez_move_imports`` CLI."""

from __future__ import print_function

import sys

from .core import exception
from . import cli

if __name__ == "__main__":
    try:
        cli.main(sys.argv[1:])
    except exception.MissingNamespaces as error:
        print(str(error), file=sys.stderr)
        sys.exit(exception.MissingNamespaces.error_code)
    except exception.InvalidInput as error:
        print(str(error), file=sys.stderr)
        sys.exit(exception.InvalidInput.error_code)
