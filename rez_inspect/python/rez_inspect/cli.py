import argparse
import os

from rez import developer_package

from .core import inspector


def parse_arguments(text):
    parser = argparse.ArgumentParser(
        description="Query any field(s) from a Rez package in your terminal.",
    )
    parser.add_argument(
        "attributes",
        nargs="+",
        help="The package data to query. e.g. ``name`` or ``name version authors``, etc.",
    )

    parser.add_argument(
        "--directory",
        default=os.getcwd(),
        help="The folder on-disk to look within for a Rez package.",
    )
    parser.add_argument(
        "--style",
        choices=sorted(inspector.STYLES.keys()),
        default=inspector.DEFAULT_STYLE,
        help="The folder on-disk to look within for a Rez package.",
    )

    return parser.parse_args(text)


def run(namespace):
    package = developer_package.DeveloperPackage.from_path(namespace.directory)
    style = inspector.get_style(namespace.style)
    inspector.print_attributes(package, namespace.attributes, style=style)
