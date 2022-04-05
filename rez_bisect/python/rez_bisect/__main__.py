"""The entry point for the :ref:`rez_bisect cli`."""

from __future__ import print_function

import logging
import sys

from .core import exception
from . import cli


if __name__ == "__main__":
    _LOGGER = logging.getLogger("rez_bisect")
    _HANDLER = logging.StreamHandler(sys.stdout)
    _HANDLER.setLevel(logging.INFO)
    _FORMATTER = logging.Formatter("%(name)s - %(levelname)s - %(message)s")
    _HANDLER.setFormatter(_FORMATTER)
    _LOGGER.addHandler(_HANDLER)
    _LOGGER.setLevel(logging.INFO)

    try:
        cli.main(sys.argv[1:])
    except exception.Base as error:
        print(
            "{error.__class__.__name__}: {error}".format(error=error), file=sys.stderr
        )
