"""Run :mod:`rez_sphinx`'s main CLI."""

from __future__ import print_function

import logging
import sys
import traceback

from . import cli
from .core import exception

_SUCCESS_EXIT_CODE = 0


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
    # TODO : Handle docbot exceptions here
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
    except exception.ConfigurationError as error:
        print(
            "Checker `rez_sphinx config check` failed. "
            "See below for details or run the command to repeat this message.",
            file=sys.stderr,
        )

        print(traceback.extract_tb(error), file=sys.stderr)

        sys.exit(error.exit_code)
    except exception.Base as error:
        print(
            "{type_}: {message}".format(
                type_=error.__class__.__name__, message=str(error)
            ),
            file=sys.stderr,
        )

        sys.exit(error.exit_code)
    except Exception:  # pylint: disable=broad-except
        text = "".join(traceback.format_exc())
        print("An unexpected error occurred. Please read the error below for details.")
        print(text, file=sys.stderr)

        sys.exit(exception.GENERIC_EXIT_CODE)

    sys.exit(_SUCCESS_EXIT_CODE)


if __name__ == "__main__":
    _setup_logger()
    main(text=sys.argv[1:])
