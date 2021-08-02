#!/usr/bin/env python

"""The main entry point for the rez-bisect CLI."""

import logging
import sys

from . import cli

_LOGGER = logging.getLogger("rez-bisect")
_HANDLER = logging.StreamHandler(sys.stdout)
_HANDLER.setLevel(logging.INFO)
_FORMATTER = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
_HANDLER.setFormatter(_FORMATTER)
_LOGGER.addHandler(_HANDLER)
_LOGGER.setLevel(logging.INFO)


cli.main(sys.argv[1:])
