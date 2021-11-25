import argparse

from .core import core_exception
from .commands.builder_registries import builder_registry
from .commands import builder as builder_, publisher as publisher_


_ARGUMENT_DELIMITER = " -- "


def _build(plug_in_namespace, remainder):
    adapter = builder_.get_plug_in(plug_in_namespace.builder)
    build_namespace = adapter.parse_arguments(remainder)

    builder_.build(build_namespace)


def _parse_arguments(text):
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

    try:
        base_arguments, remainder = text.index(_ARGUMENT_DELIMITER)
    except ValueError:
        raise core_exception.MissingDelimiter('You must add "{_ARGUMENT_DELIMITER}" somewhere in the command. See --help for details.'.format(_ARGUMENT_DELIMITER=_ARGUMENT_DELIMITER))

    return parser.parse_args(base_arguments), remainder


def _publish(namespace):
    raise NotImplementedError('Need to write this')


def main(text):
    """Parse the given input and run the given command.

    Args:
        text (list[str]):
            The user-provided command, Each string is assumed to be space
            separated. e.g. ["publish", "github", "documentation/build"].

    """
    namespace, remainder = _parse_arguments(text)
    namespace.execute(namespace, remainder)
