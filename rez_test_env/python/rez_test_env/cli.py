#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Parse the user's input from the CLI and run a `rez-env` command using it."""

from __future__ import print_function

import argparse
import os

from .core import environment, exceptions

try:
    from rez import packages_ as packages
except ImportError:
    from rez import packages


def _add_tests_parameter(parser):
    """Add a ``tests`` positional parameter to an argparse object.

    Args:
        parser (:class:`argparse.ArgumentParser`): The parser to append to.

    """
    parser.add_argument(
        "tests",
        nargs="*",
        help="The test requirements to append to the package request.",
    )

    parser.add_argument(
        "--shell",
        help="The terminal used for a new Rez environment. Defaults to the current shell.",
    )


def _multi_requester(arguments):
    """Get an environment using the user's request.

    Args:
        arguments (:class:`argparse.Namespace`): The parsed user input.

    """
    environment.run_from_request(
        arguments.package_request,
        arguments.tests,
        shell=arguments.shell,
    )


def _parse_arguments(text):
    """Split the user's request into the Rez package + Rez test(s).

    Args:
        text (list[str]):
            The space-separated input from the CLI. Usually from :obj:`sys.argv`.

    Returns:
        :class:`argparse.Namespace`: The parsed arguments.

    """
    parser = argparse.ArgumentParser(description="")

    sub_parsers = parser.add_subparsers(
        title="sub-parsers",
        description="All commands within rez_test_env.",
    )

    multi_requester = sub_parsers.add_parser(
        "request", description="Make any arbitrary Rez package request."
    )
    multi_requester.add_argument(
        "package_request", help="The Rez package to make an environment for."
    )
    _add_tests_parameter(multi_requester)
    multi_requester.set_defaults(execute=_multi_requester)

    pwd_requester = sub_parsers.add_parser(
        "directory", description="Use a given directory's Rez package."
    )
    pwd_requester.add_argument(
        "--directory",
        default=os.getcwd(),
        help="The directory to search within for a Rez package. This defaults to $PWD",
    )
    pwd_requester.add_argument(
        "-b",
        "--build-requires",
        action="store_true",
        help="If enabled, include all requirements in `build_requires` to the resolve",
    )
    pwd_requester.add_argument(
        "-p",
        "--private-build-requires",
        action="store_true",
        help="If enabled, include all requirements in `private_build_requires` to the resolve",
    )

    _add_tests_parameter(pwd_requester)
    pwd_requester.set_defaults(execute=_pwd_requester)

    query_tests = sub_parsers.add_parser(
        "query-tests", description="Get the names of the available Rez tests."
    )
    query_tests.add_argument(
        "--directory",
        default=os.getcwd(),
        help="The directory to search within for a Rez package. This defaults to $PWD",
    )
    query_tests.set_defaults(execute=_query_tests)

    return parser.parse_args(text)


def _pwd_requester(arguments):
    """Get an environment using the nearest Rez package.

    Args:
        arguments (:class:`argparse.Namespace`): The parsed user input.

    Raises:
        :class:`.NoValidPackageFound`: If the given directory isn't within a Rez package.

    """
    package = environment.get_nearest_rez_package(arguments.directory)

    if not package:
        raise exceptions.NoValidPackageFound(
            'Directory "{arguments.directory}" is not inside of a Rez package.'.format(
                arguments=arguments
            )
        )

    environment.run_from_package(
        package,
        arguments.tests,
        shell=arguments.shell,
        build_requires=arguments.build_requires,
        private_build_requires=arguments.private_build_requires,
    )


def _query_tests(arguments):
    """Print the Rez tests of the package under `arguments`.

    Args:
        arguments (:class:`argparse.Namespace`): The parsed user input.

    Raises:
        :class:`.NoValidPackageFound`: If no Rez package could be found.

    """
    package = packages.get_developer_package(arguments.directory)

    if not packages:
        if not package:
            raise exceptions.NoValidPackageFound(
                'Directory "{arguments.directory}" is not inside of a Rez package.'.format(
                    arguments=arguments
                )
            )

    for name in sorted((package.tests or dict()).keys(), reverse=True):
        print(name)


def main(text):
    """Split the user's request into the Rez package + Rez test(s).

    Args:
        text (list[str]):
            The space-separated input from the CLI. Usually from :obj:`sys.argv`.

    """
    arguments = _parse_arguments(text)
    arguments.execute(arguments)
