"""The entry point for :ref:`rez_sphinx` on the terminal."""

import argparse
import logging
import os

from rez_utilities import finder

from .commands import initer
from .core import exception, path_control

_LOGGER = logging.getLogger(__name__)


def _init(namespace):
    """Create a Sphinx project, rooted at ``namespace``.

    Args:
        namespace (:class:`argparse.Namespace`):
            The parsed user content. It contains all of the necessary
            attributes to generate Sphinx documentation.

    """
    directory = path_control.expand_path(namespace.directory)
    _LOGGER.debug('Found "%s" directory.', directory)
    package = finder.get_nearest_rez_package(directory)

    if not package:
        raise exception.NoPackageFound(
            'Directory "{directory}" is not in a Rez package. Cannot continue.'.format(
                directory=directory
            )
        )

    _LOGGER.debug('Found "%s" Rez package.', package.name)

    documentation_root = os.path.normpath(os.path.join(directory, namespace.documentation_root))
    _LOGGER.debug('Setting up documentation in "%s" folder.', documentation_root)

    initer.init(documentation_root)


def main(text):
    """Parse and run ``text``, the user's terminal arguments for :rez:`rez_sphinx`.

    Args:
        text (list[str]):
            The user-provided arguments to run via :ref:`rez_sphinx`.
            This is usually space-separated CLI text like
            ``["init", "--directory", "/path/to/rez/package"]``.

    """
    namespace = parse_arguments(text)
    run(namespace)


def parse_arguments(text):
    """Check the given text for validity and, if valid, parse + return the result.

    Args:
        text (list[str]):
            The user-provided arguments to run via :ref:`rez_sphinx`.
            This is usually space-separated CLI text like
            ``["init", "--directory", "/path/to/rez/package"]``.

    Returns:
        :class:`argparse.Namespace`: The parsed user content.

    """
    parser = argparse.ArgumentParser(
        description="Auto-generate Sphinx documentation for Rez packages.",
    )

    sub_parsers = parser.add_subparsers()
    init = sub_parsers.add_parser(
        "init", description="Set up a Sphinx project in a Rez package."
    )
    init.set_defaults(execute=_init)
    init.add_argument(
        "directory",
        nargs="?",
        default=os.getcwd(),
        help="The folder to search for a Rez package. Defaults to the current working directory.",
    )
    init.add_argument(
        "--documentation-root",
        default="documentation",
        help="The"
    )

    return parser.parse_args(text)


def run(namespace):
    """Run the selected subparser.

    Args:
        namespace (:class:`argparse.Namespace`):
            The parsed user content. It should have a callable method called
            "execute" which takes ``namespace`` as its only argument.

    """
    namespace.execute(namespace)
