"""Traverse and print package dependencies from the user's input."""

from __future__ import print_function

import logging
import sys

from . import cli
from ._core import exception

_LOGGER = logging.getLogger("rez_dependency")
_HANDLER = logging.StreamHandler(sys.stdout)
_HANDLER.setLevel(logging.INFO)
_FORMATTER = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
_HANDLER.setFormatter(_FORMATTER)
_LOGGER.addHandler(_HANDLER)
_LOGGER.setLevel(logging.INFO)


try:
    cli.main(sys.argv[1:])
except exception.Base as error:
    print("{error.__class__.__name__}: {error}".format(error=error), file=sys.stderr)

    sys.exit(error.code)
