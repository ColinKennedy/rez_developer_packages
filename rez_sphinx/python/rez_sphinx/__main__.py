"""Run :mod:`rez_sphinx`'s main CLI."""

from __future__ import print_function

import logging
import sys
import traceback

from . import cli
from .core import exception


def _setup_logger():
    """Add stdout logging while the CLI is running."""
    logger = logging.getLogger(__name__)
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.INFO)
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)


def main(text):
    """Parse and run the users's given parameters.

    Args:
        text (list[str]):
            The user-provided arguments to run via :ref:`rez_sphinx`.
            This is usually space-separated CLI text like
            ``["init", "--directory", "/path/to/rez/package"]``.

    """
    try:
        cli.main(text)
    except exception.Base as error:
        print(
            "{type_}: {message}".format(
                type_=error.__class__.__name__, message=str(error)
            ),
            file=sys.stderr,
        )
    except Exception:  # pylint: disable=broad-except
        print("An unexpected error occurred. Please read the error below for details.")
        text = "".join(traceback.format_exc())
        print(text, file=sys.stderr)


if __name__ == "__main__":
    _setup_logger()
    main(text=sys.argv[1:])
