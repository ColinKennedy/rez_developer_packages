#!/usr/bin/env python

"""The main entry point for the rez-bisect CLI.

This module is ran any time the user calls `python -m rez_bisect`.

"""

import logging
import sys

from .core import exception
from . import cli

_LOGGER = logging.getLogger("rez-bisect")
_HANDLER = logging.StreamHandler(sys.stdout)
_HANDLER.setLevel(logging.INFO)
_FORMATTER = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
_HANDLER.setFormatter(_FORMATTER)
_LOGGER.addHandler(_HANDLER)
_LOGGER.setLevel(logging.INFO)

try:
    cli.main(sys.argv[1:])
except exception.BaseException as error:
    print(str(error), file=sys.stderr)

    sys.exit(error.code)
