"""The module which parses user input from `rez_docbot` and runs a user command."""

import argparse

from .commands import builder as builder_
from .commands import publisher as publisher_
from .commands.builder_registries import builder_registry
from .core import core_exception

_ARGUMENT_DELIMITER = " -- "


def _build(full_namespace):
    """Perform the `rez_docbot build` command, using `full_namespace`.

    Args:
        full_namespace (:class:`argparse.ArgumentParser`):
            The parsed user input. A portion of it will be passed directly to a
            :class:`.BuilderPlugin`.

    """
    adapter = builder_registry.get_plugin(full_namespace.builder)
    build_namespace = adapter.parse_arguments(full_namespace.extra_arguments)
    adapter.build(build_namespace)


def _parse_arguments(text):
    """Parse the user-input into something that this Python package can use.

    Args:
        text (list[str]):
            Text separated by spaces, e.g. ["github", "--", "documentation/build"]

    Returns:
        :class:`argparse.ArgumentParser`: The parsed output.

    """
    parser = argparse.ArgumentParser(description="The main CLI which contains sub-commands.")
    sub_parsers = parser.add_subparsers()
    builder = sub_parsers.add_parser("build")
    builder.add_argument(
        "builder",
        help="The plugin to build with. e.g. `sphinx`.",
        choices=builder_registry.get_allowed_plugins(),
    )
    builder.set_defaults(execute=_build)

    publisher = sub_parsers.add_parser(
        "publish",
        help="Send data to some external location. e.g. Send to GitHub.",
    )
    publisher.set_defaults(execute=_publish)

    # TODO : Add auto-completion for this, maybe
    builder.add_argument(
        "--N0",
        dest="extra_arguments",
        nargs='*',
        help=argparse.SUPPRESS,
    )

    publisher.add_argument(
        "--N0",
        dest="extra_arguments",
        nargs='*',
        help=argparse.SUPPRESS,
    )

    return parser.parse_args(text)


def _publish(namespace):
    raise NotImplementedError('Need to write this')


def main(text):
    """Parse the given input and run the given command.

    Args:
        text (list[str]):
            The user-provided command, Each string is assumed to be space
            separated. e.g. ["publish", "github", "documentation/build"].

    """
    namespace = _parse_arguments(text)
    namespace.execute(namespace, remainder)
