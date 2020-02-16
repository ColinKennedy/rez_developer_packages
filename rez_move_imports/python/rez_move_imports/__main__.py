"""The entry point for the ``rez_move_imports`` CLI."""

import sys

from . import cli

if __name__ == "__main__":
    cli.main(sys.argv[1:])
