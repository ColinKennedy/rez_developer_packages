from __future__ import print_function

import sys

from .core import core_exception
from . import cli


if __name__ == "__main__":
    try:
        cli.main(sys.argv[1:])
    except core_exception.Base as error:
        print(str(error), file=sys.stderr)

        sys.exit(error.get_error_code())
