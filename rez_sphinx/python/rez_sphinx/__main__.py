"""Run :mod:`rez_sphinx`'s main CLI."""

from __future__ import print_function

import logging
import sys
import traceback

from . import cli
from .core import exception

_SUCCESS_EXIT_CODE = 0


def _is_docbot_exception(error):
    """bool: Check if ``error`` comes from :ref:`rez_docbot`."""
    try:
        from rez_docbot import api
    except ImportError:
        # It's disabled. Just ignore it.
        return False

    return isinstance(error, api.CoreException)


def _setup_logger():
    """Add stdout logging while the CLI is running."""
    logger = logging.getLogger("rez_sphinx")
    handler = logging.StreamHandler(sys.stderr)
    handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter("%(name)s - %(levelname)s - %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.WARNING)


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
    except exception.SphinxExecutionError as error:
        # TODO : Make sure these actually look good
        print(
            "Something errored while Sphinx was running.\n"
            "See the error below for details.",
            file=sys.stderr,
        )
        print(str(error))

        sys.exit(error.exit_code)
    except exception.Base as error:
        print(
            "{type_}: {message}".format(
                type_=error.__class__.__name__, message=str(error)
            ),
            file=sys.stderr,
        )

        sys.exit(error.exit_code)
    except Exception as error:  # pylint: disable=broad-except
        if _is_docbot_exception(error):
            print("docbot: {error}".format(error=error), file=sys.stderr)

            sys.exit(exception.GENERIC_EXIT_CODE)

            return

        text = "".join(traceback.format_exc())
        print("An unexpected error occurred. Please read the error below for details.")
        print(text, file=sys.stderr)

        sys.exit(exception.GENERIC_EXIT_CODE)

    sys.exit(_SUCCESS_EXIT_CODE)


if __name__ == "__main__":
    _setup_logger()
    main(text=sys.argv[1:])
