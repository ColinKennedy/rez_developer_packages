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

    def _add_argument(parser):
        parser.add_argument(
            "extra_arguments",
            nargs=argparse.REMAINDER,
            help=argparse.SUPPRESS,
        )

    parser = argparse.ArgumentParser(
        description="The main CLI which contains sub-commands."
    )
    sub_parsers = parser.add_subparsers()
    builder = sub_parsers.add_parser("build")
    builder.add_argument(
        "builder",
        help="The plugin to build with. e.g. `sphinx`.",
        choices=builder_registry.get_plugin_names(),
    )
    builder.set_defaults(execute=_build)

    publisher = sub_parsers.add_parser(
        "publish",
        help="Send data to some external location. e.g. Send to GitHub.",
    )
    publisher.set_defaults(execute=_publish)

    # TODO : Add auto-completion for this, maybe
    _add_argument(builder)
    _add_argument(publisher)

    return parser.parse_args(text)


def _publish(namespace):
    """Send the build documentation to an external location (e.g. GitHub).

    Args:
        namespace (:class:`argparse.ArgumentParser`):
            The user-parsed input. It typically it points to a folder of built
            documentation and may also include other details needed for
            publishing.

    """
    raise NotImplementedError("Need to write this")


def main(text):
    """Parse the given input and run the given command.

    Args:
        text (list[str]):
            The user-provided command, Each string is assumed to be space
            separated. e.g. ["publish", "github", "documentation/build"].

    """
    namespace = _parse_arguments(text)
    namespace.execute(namespace)
