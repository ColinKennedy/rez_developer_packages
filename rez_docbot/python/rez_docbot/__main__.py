"""Run the CLI for `rez_docbot` - run a build, publish, etc command."""

from __future__ import print_function

import sys

from . import cli
from .core import core_exception

if __name__ == "__main__":
    try:
        cli.main(sys.argv[1:])
    except core_exception.Base as error:
        print(str(error), file=sys.stderr)

        sys.exit(error.get_error_code())
