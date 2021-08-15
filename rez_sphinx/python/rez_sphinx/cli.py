import argparse


def _builder(arguments):
    raise NotImplementedError()


def _checker(arguments):
    raise NotImplementedError()


def _creator(arguments):
    raise NotImplementedError()


def _publisher(arguments):
    raise NotImplementedError()


def _parse_arguments(text):
    parser = argparse.ArgumentParser(description="Create, build, or publish Sphinx documentation for any Rez package.")
    subparsers = parser.add_subparsers(help="The available commands for this Sphinx plugin.")
    builder = subparsers.add_parser("build", help="Build the Sphinx documentation into HTML.")
    builder.set_defaults(execute=_builder)
    checker = subparsers.add_parser("check", help="Make sure your Rez package + documentation are both healthy.")
    checker.set_defaults(execute=_checker)
    creator = subparsers.add_parser("create", help="Initialize a Sphinx documentation environment in your Rez package.")
    creator.set_defaults(execute=_creator)
    publisher = subparsers.add_parser("publisher", help="Submit your documentation to a remote server (e.g. GitHub)")
    publisher.set_defaults(execute=_publisher)

    return parser.parse_args(text)


def main(text):
    arguments = _parse_arguments(text)
    arguments.execute(arguments)
