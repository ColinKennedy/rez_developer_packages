import argparse

from rez.config import config

from ._core import converter as converter_, installer as installer_


def _add_destination_argument(parser):
    parser.add_argument(
        "--destination",
        default=config.local_packages_path,
        help="The path to place any generated Rez packages.",
    )


def _add_name_argument(parser):
    parser.add_argument("name", help='The name of the Yum package. e.g. "gcc".')


def _convert(namespace):
    converter_.convert(namespace.name, destination=namespace.destination)


def _install(namespace):
    installer_.install(namespace.name, destination=namespace.destination)


def main(text):
    # """Run the main execution of the script."""
    namespace = parse_arguments(text)
    run(namespace)


def parse_arguments(text):
    parser = argparse.ArgumentParser(
        description="Generate Rez packages using Yum packages."
    )
    subparsers = parser.add_subparsers()

    installer = subparsers.add_parser(
        "install",
        description="Download + Install Yum RPMs.",
    )
    installer.set_defaults(execute=_install)
    _add_destination_argument(installer)
    _add_name_argument(installer)

    converter = subparsers.add_parser(
        "convert",
        description="Change a RPM into a proper Rez package.",
    )
    converter.set_defaults(execute=_convert)
    _add_destination_argument(converter)
    _add_name_argument(converter)

    return parser.parse_args(text)


def run(namespace):
    namespace.execute(namespace)
