"""The entry point for :ref:`rez_sphinx` on the terminal."""

import argparse
import logging
import operator
import shlex
import os

from rez_utilities import finder
from rez.cli import _complete_util

from .commands import builder, initer
from .core import api_builder, exception, path_control

_LOGGER = logging.getLogger(__name__)


def _add_directory_argument(parser):
    """Make ``parser`` include a positional argument pointing to a file path on-disk.

    Args:
        parser (:class:`argparse.ArgumentParser`): The instance to modify.

    """
    parser.add_argument(
        "directory",
        nargs="?",
        default=os.getcwd(),
        help="The folder to search for a Rez package. "
        "Defaults to the current working directory.",
    )


def _build(namespace):
    """Build Sphinx documentation, using details from ``namespace``."""
    builder.build(namespace.directory, api_mode=namespace.api_documentation)


def _init(namespace):
    """Create a Sphinx project, rooted at ``namespace``.

    Args:
        namespace (:class:`argparse.Namespace`):
            The parsed user content. It contains all of the necessary
            attributes to generate Sphinx documentation.

    """
    _split_init_arguments(namespace)

    directory = namespace.directory
    _LOGGER.debug('Found "%s" directory.', directory)
    package = finder.get_nearest_rez_package(directory)

    if not package:
        raise exception.NoPackageFound(
            'Directory "{directory}" is not in a Rez package. Cannot continue.'.format(
                directory=directory
            )
        )

    _LOGGER.debug('Found "%s" Rez package.', package.name)

    documentation_root = os.path.normpath(
        os.path.join(directory, namespace.documentation_root)
    )
    initer.init(
        package, documentation_root, quick_start_options=namespace.quick_start_arguments
    )


def _set_up_build(sub_parsers):
    """Add :ref:`rez_sphinx build` CLI parameters.

    Args:
        sub_parsers (:class:`argparse._SubParsersAction`):
            A collection of parsers which the :ref:`rez_sphinx build`
            will be appended onto.

    """
    build = sub_parsers.add_parser(
        "build", description="Compile Sphinx documentation from a Rez package."
    )
    build.required = True
    _add_directory_argument(build)
    choices = sorted(api_builder.MODES, key=operator.attrgetter("label"))
    build.add_argument(
        "--api-documentation",
        choices=[mode.label for mode in choices],
        default=api_builder.FULL_AUTO.label,
        help="When building, API .rst files can be generated for your Python files.\n\n"
        + "\n".join(
            "{mode.label}: {mode.description}".format(mode=mode) for mode in choices
        ),
    )
    build.set_defaults(execute=_build)


def _set_up_init(sub_parsers):
    """Add :ref:`rez_sphinx init` CLI parameters.

    Args:
        sub_parsers (:class:`argparse._SubParsersAction`):
            A collection of parsers which the :ref:`rez_sphinx init`
            will be appended onto.

    """
    init = sub_parsers.add_parser(
        "init", description="Set up a Sphinx project in a Rez package."
    )
    init.required = True
    init.add_argument(
        "--quickstart-arguments",
        dest="quick_start_arguments",
        help='Anything you\'d like to send for sphinx-quickstart. e.g. "--ext-coverage"',
    )
    init.set_defaults(execute=_init)
    _add_directory_argument(init)
    init.add_argument(
        "--documentation-root",
        default="documentation",
        help="The directory where you want source documentation (.rst files) to be placed.",
    )

    remainder = init.add_argument(
        "remainder",
        nargs="*",
        help=argparse.SUPPRESS,
    )
    remainder.completer = _complete_util.SequencedCompleter(
        "remainder",
        _complete_util.ExecutablesCompleter,
        _complete_util.FilesCompleter(),
    )


def _split_init_arguments(namespace):
    """Conform ``namespace`` attributes so other functions can use it more easily.

    Warning:
        This function will modify ``namespace`` in-place.

    Args:
        namespace (:class:`argparse.Namespace`):
            The parsed user content. It contains all of the necessary
            attributes to generate Sphinx documentation.

    """
    namespace.quick_start_arguments = shlex.split(namespace.quick_start_arguments or "")

    if not namespace.remainder:
        return

    namespace.quick_start_arguments.extend(namespace.remainder)


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

    _set_up_build(sub_parsers)
    _set_up_init(sub_parsers)

    # TODO : Fix the error where providing no subparser command
    # DOES NOT show the help message
    return parser.parse_args(text)


def run(namespace, modify=True):
    """Run the selected subparser.

    Args:
        namespace (:class:`argparse.Namespace`):
            The parsed user content. It should have a callable method called
            "execute" which takes ``namespace`` as its only argument.
        modify (bool, optional):
            If True, run extra calls directly modifying ``namespace``
            before calling the main execution function. If False, just
            take ``namespace`` directly as-is.

    """
    if modify:
        namespace.directory = path_control.expand_path(namespace.directory)

    namespace.execute(namespace)
