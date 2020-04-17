#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The main module that controls the command-line's interface."""

from __future__ import print_function

import argparse
import functools
import copy
import fnmatch
import logging
import operator
import os
import sys

import six
from python_compatibility import imports, wrapping
from rez.config import config
from rez_utilities import inspection

from .core import cli_constant, registry, worker
from .core.gitter import github_user

_LOGGER = logging.getLogger(__name__)


def __gather_package_data(arguments):
    """Use the user-provided CLI arguments to find Rez packages.

    Args:
        arguments (:class:`argparse.ArgumentParser`):
            The packages to ignore, paths to search for packages,
            the command to use for searching, and other important
            searching-related details.

    Returns:
        All of the data needed for the `__report` and `__run` functions.

    """
    ignore_patterns, packages_path, search_packages_path = _resolve_arguments(
        arguments.ignore_patterns,
        arguments.packages_path,
        arguments.search_packages_path,
    )
    rez_packages = set(arguments.rez_packages)

    package_finder = registry.get_package_finder(arguments.command)

    found_packages = []
    packages, invalid_packages, skips = package_finder(paths=packages_path + search_packages_path)

    for package in packages:
        if rez_packages and package.name not in rez_packages:
            skips.append(package)
        else:
            found_packages.append(package)

    ignored_packages, other_packages = _split_the_ignored_packages(
        found_packages, ignore_patterns
    )

    return ignored_packages, other_packages, invalid_packages, skips


def __report(arguments, _):
    """Print out every package and its status information.

    This function prints out

    - Packages that were found as "invalid"
    - Packages that were skipped automatically
    - Packages that were ignored explicitly (by the user)

    Args:
        arguments (:class:`argparse.Namespace`):
            The base user-provided arguments from command-line.
        _ (:class:`argparse.Namespace`):
            An un-used argument for this function.

    """
    ignored_packages, other_packages, invalid_packages, skips = __gather_package_data(arguments)

    packages, invalids = worker.report(
        other_packages,
        maximum_repositories=arguments.maximum_repositories,
        maximum_rez_packages=arguments.maximum_rez_packages,
    )

    invalids.extend(invalid_packages)

    _print_ignored(ignored_packages)
    print("\n")
    _print_skips(skips, arguments.verbose)
    print("\n")
    _print_invalids(invalids, arguments.verbose)
    print("\n")
    _print_missing(packages, arguments.verbose)

    sys.exit(0)


def __run(arguments, command_arguments):  # pylint: disable=too-many-locals
    """Execute a plugin command on any package that needs it.

    Args:
        arguments (:class:`argparse.Namespace`):
            The base user-provided arguments from command-line.
        command_arguments (:class:`argparse.Namespace`):
            The registered command's parsed arguments.

    """
    ignored_packages, other_packages, invalid_packages, skips = __gather_package_data(arguments)

    command = registry.get_command(arguments.command)

    packages, un_ran, invalids = worker.run(
        functools.partial(command.run, arguments=command_arguments),
        other_packages,
        maximum_repositories=arguments.maximum_repositories,
        maximum_rez_packages=arguments.maximum_rez_packages,
        keep_temporary_files=arguments.keep_temporary_files,
        temporary_directory=arguments.temporary_directory,
    )

    invalids.extend(invalid_packages)

    # TODO : Change `Skip` into a class and make it the same interface as an exception
    # so that I can easily print both types at the same time, here
    #
    bads = invalids + skips

    if bads:
        print("Some packages are invalid or had to be skipped.")
        print("\n")
        print(sorted(package.name for package in bads))

    if un_ran:
        print("These packages could not be run on:")

        for package, error in sorted(un_ran, key=_get_package_name):
            print(
                "{package.name}: {error}".format(
                    package=package, error=str(error) or "No found error message"
                )
            )

        sys.exit(cli_constant.UN_RAN_PACKAGES_FOUND)

    if packages:
        print("These packages were modified successfully:")

        for package in sorted(packages, key=operator.attrgetter("name")):
            print(package.name)


def __make_git_users(arguments):
    """Write a cache of GitHub users to-disk.

    Args:
        arguments (:class:`argparse.Namespace`):
            The GitHub token, path to write to disk, and any other important details.

    """
    github_user.write_cache(
        arguments.path,
        arguments.token,
        base_url=arguments.base_url,
        verify=arguments.ssl_no_verify,
        maximum=arguments.maximum_users,
    )

    print(
        'GitHub users were written to "{arguments.path}" successfully.'
        "".format(arguments=arguments)
    )

    sys.exit(0)


def _split_the_ignored_packages(packages, patterns):
    """Get the "user-ignored" Rez packages.

    Args:
        packages (iter[:class:`rez.packages_.Package`]):
            The Rez packages that may or may not need to be ignored.
        patterns (list[str]):
            All glob patterns that are used to find packages to ignore.
            If a Rez package's name matches even one of the strings in
            `patterns` then the package is ignored.

    Returns:
        tuple[set[:class:`rez.packages_.Package`], set[:class:`rez.packages_.Package`]]:
            The Rez packages to ignore, followed by the Rez packages to
            not ignore.

    """
    ignored = set()
    non_ignored = set()

    for package in packages:
        for pattern in patterns:
            if fnmatch.fnmatch(package.name, pattern):
                ignored.add((package, pattern))

                break
        else:
            non_ignored.add(package)

    return ignored, non_ignored


def _resolve_arguments(patterns, packages_path, search_packages_path):
    """Convert user-provided data into glob expressions.

    Args:
        patterns (iter[str]):
            The strings to resolve into glob patterns. These strings
            could be glob expressions by themselves or they could
            be paths to files on-disk that contain glob expressions
            (one-expression-by-line).
        packages_path (str or list[str]):
            The Rez package directories that "run" or "report" will run
            on. It could be a path-separated string like "/foo:/bar" or
            a list of strings, like ["/foo", "/bar"].
        search_packages_path (str or list[str]):
            Extra Rez package directories that will be used to help
            resolve packages found in `packages_path`. The Rez packages
            found here will not be processed using "run" or "report".

    Returns:
        tuple[set[str], list[str]]:
            The resolved glob expressions and the paths to search for
            Rez packages.

    """

    def _read_patterns(path):
        try:
            with open(path, "r") as handler:
                return set(handler.read().splitlines())
        except IOError:
            return set()

    ignore_patterns = set()

    for item in patterns:
        if os.path.isfile(item) or os.path.isabs(item):
            # This happens in 2 scenarios
            # 1. The user-given pattern is actually a path on-disk
            # 2. The user does bash process substitution (e.g.
            #    `rez-batch-process report --ignore-patterns <(cat patterns.txt)`)
            #
            ignore_patterns.update(_read_patterns(item))
        else:
            ignore_patterns.add(item)

    if isinstance(packages_path, six.string_types):
        packages_path = packages_path.split(os.pathsep)

    if isinstance(search_packages_path, six.string_types):
        search_packages_path = search_packages_path.split(os.pathsep)

    return ignore_patterns, packages_path, search_packages_path


def _get_package_name(item):
    """str: Sort a package / error pair by the name of each Rez package."""
    package = item[0]

    return package.name


def _print_ignored(packages):
    """Print every package as "ignored".

    Args:
        packages (iter[:class:`rez.packages_.Package`, str]):
            The Rez package and the glob pattern that it matched against.

    """
    if not packages:
        print("## No Rez package was set to be ignored")
        print("No data found")

        return

    print("## Every package in this list was explicitly set to ignored by the user")

    for package, pattern in sorted(packages, key=_get_package_name):
        print(
            'Package: {package.name} - Pattern: "{pattern}"'.format(
                package=package, pattern=pattern
            )
        )


def _print_invalids(invalids, verbose):
    """Print out the errors that were found.

    Args:
        invalids (iter[:class:`.CoreException`]): The exceptions that were
            raised while searching for packages. Each error contains the
            package, path on-disk to that package, and error message
            that was found.
        verbose (bool): If True, print out as much information as possible.
            If False, print out concise "one-liner" information.

    """
    if not invalids:
        print("## No Rez package was set as invalid.")
        print("Nothing is invalid. Which is a good thing!")

        return

    print("## Some packages were marked as invalid. Here's why:")

    template = "{package.name}: {message}"

    if verbose:
        template = "{package.name}: {path} {message}: {full}"

    for message in sorted(
        (
            template.format(
                package=error.get_package(),
                path=error.get_path(),
                message=str(error),
                full=error.get_full_message(),
            )
            for error in invalids
        )
    ):
        print(message)


def _print_missing(packages, verbose):
    """Print all Rez packages that should be run on.

    Args:
        packages (iter[:class:`rez.packages`]): The Rez packages that
            describe a Python module / package.
        verbose (bool): If True, print out as much information as possible.
            If False, print out concise "one-liner" information.

    """
    if not packages:
        print("## No Rez packages were found.")
        print("No data found")

        return

    print("## Your command affects these Rez packages.")

    template = "{package.name}"

    if verbose:
        template = "{package.name}: {path}"

    for line in sorted(
        template.format(package=package, path=inspection.get_package_root(package))
        for package in packages
    ):
        print(line)


def _print_skips(skips, verbose):
    """Print the Rez packages that were skipped automatically by this tool.

    Skipped packages differ from "invalid" packages in that they are
    "valid Rez packages but just don't need the command run on". Ignored
    packages are Rez packages that the user explicitly said to not
    process. Skipped packages are packages that the user may have meant
    to process but this tool could not (for some reason or another).

    Args:
        skips (:attr:`.Skip`): A collection of Rez package, path on-disk, and a
            message the explains a reason for the skip.
        verbose (bool): If True, print out as much information as possible.
            If False, print out concise "one-liner" information.

    """
    if not skips:
        print("## No packages were skipped")
        print("Every found Rez package can be processed by the command.")

        return

    print("## Packages were skipped from running a command. Here's the full list:")

    template = "{issue.package.name}: {issue.reason}"

    if verbose:
        template = "{issue.package.name}: {issue.path}: {issue.reason}"

    for issue in skips:
        print(template.format(issue=issue))


def _add_arguments(parser):
    """Add common arguments to the given command-line `parser`.

    Args:
        parser (:class:`argparse.ArgumentParser`):
            The user-provided parser that will get options appended to it.

    """
    parser.add_argument(
        "command",
        help='The plugin to run. e.g. "shell".',
        choices=sorted(registry.get_command_keys()),
    )

    parser.add_argument(
        "-x",
        "--maximum-repositories",
        default=sys.maxint,
        type=int,
        help='If a value of `2` is used, it means "Only search 2 repositories '
        'for Rez packages to run on, at most".',
    )

    parser.add_argument(
        "-z",
        "--maximum-rez-packages",
        default=sys.maxint,
        type=int,
        help='If a value of `2` is used, it means "Only search for 2 Rez packages '
        'to run some comm on, at most".',
    )

    parser.add_argument(
        "-p",
        "--packages-path",
        default=[config.release_packages_path],  # pylint: disable=no-member
        help="A `{os.pathsep}` separated list of paths that report/run will be run on. "
        "If not defined, `rez.config.config.release_packages_path` is used, instead.".format(
            os=os
        ),
    )

    parser.add_argument(
        "-s",
        "--search-packages-path",
        default=[config.release_packages_path],  # pylint: disable=no-member
        help="A `{os.pathsep}` separated list of paths to search for Rez package dependencies. "
        "If not defined, `rez.config.config.release_packages_path` is used, instead.".format(
            os=os
        ),
    )

    parser.add_argument(
        "-i",
        "--ignore-patterns",
        default=[],
        nargs="*",
        help="A set of glob expressions or a file to a set of glob expressions. "
        "If a Rez package name matches one of "
        "these, it will not be run on.",
    )

    parser.add_argument(
        "-k",
        "--keep-temporary-files",
        action="store_true",
        help="If added, do not delete any temporary files that are generated during this run.",
    )

    parser.add_argument(
        "-r",
        "--rez-packages",
        default=set(),
        nargs="+",
        help="The names of Rez packages to process. If no names are given, "
        "every Rez package that is found will be processed.",
    )

    parser.add_argument(
        "-t",
        "--temporary-directory",
        help="A folder on-disk that will be used to clone git repositories.",
    )


def _process_help(text):
    """Check which help message the user actually wants to print out to the shell.

    The concept behind this function is a bit weird.

    Imagine you have 3 calls to ``rez_batch_process``

    python -m rez_batch_process --help
    python -m rez_batch_process run --help
    python -m rez_batch_process run shell --help

    The first should print the choices "report" and "run".
    The second should print the arguments for "run".
    The third should print the arguments for the dynamic plugin for "shell".

    Unfortunately, that's not how it works. If the "--help" flag is
    listed anywhere after the ``python -m rez_batch_process run`` part,
    it prints the help message for run. The help message for "shell" is
    never shown.

    This function fixes this problem, by detecting the user's intent and
    slightly modifying the `text` input so that argparse stays happy and
    the right help message is printed.

    Args:
        text (list[str]): User provided arguments (that will be modified).

    Raises:
        RuntimeError: If somehow `text` is invalid.

    Returns:
        tuple[list[str], bool]:
            The modified text + a True / False, which represents whether
            the plugin's help needs to be displayed (or something else).

    """
    text = copy.copy(text)

    found_text = ""

    if "--help" in text:
        found_text = "--help"
    elif "-h" in text:
        found_text = "-h"

    if not found_text:
        return text, False

    subparser_index = -1

    for key in ("report", "run", "make-git-users"):
        try:
            subparser_index = text.index(key)
        except ValueError:
            pass

    if subparser_index == -1:
        raise RuntimeError(
            'Text "{text}" is not a registered command.'.format(text=text)
        )

    if text.index(found_text) - 1 > subparser_index:
        text.remove(found_text)

    return text, True


def parse_arguments(text):
    """Add commands such as "report" and "run" which can detect / run.

    Returns:
        tuple[:class:`argparse.Namespace`, :class:`argparse.Namespace`]:
            The base user-provided arguments from command-line followed
            by the registered command's parsed arguments.

    """
    text, needs_subparser_help = _process_help(text)

    parser = argparse.ArgumentParser(
        description="Find Rez packages to change using a command."
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Print debug messages when this flag is included.",
    )

    sub_parsers = parser.add_subparsers(
        title="commands", description="The available command that can be run."
    )

    reporter = sub_parsers.add_parser("report")
    reporter.set_defaults(execute=__report)
    _add_arguments(reporter)

    runner = sub_parsers.add_parser("run")
    runner.set_defaults(execute=__run)
    _add_arguments(runner)

    git_users_command = sub_parsers.add_parser("make-git-users")
    git_users_command.set_defaults(execute=__make_git_users)
    git_users_command.add_argument(
        "token",
        help="The authentication token to the remote git repository (GitHub, bitbucket, etc).",
    )
    git_users_command.add_argument(
        "path", help="The found users will be written to this JSON file path."
    )
    git_users_command.add_argument(
        "-m",
        "--maximum-users",
        default=sys.maxint,
        type=int,
        help="This integer represents that maximum number of users to query. "
        "Set this value low to avoid long wait times.",
    )
    git_users_command.add_argument(
        "-b",
        "--base-url",
        help="If you are authenticating to a non-standard remote "
        "(e.g. GitHub enterprise), use this flag to provide the URL.",
    )
    git_users_command.add_argument(
        "-s", "--ssl-no-verify", action="store_false", help="Disable SSL verification"
    )

    arguments, unknown_arguments = parser.parse_known_args(text)

    if arguments.execute == __make_git_users:
        if needs_subparser_help:
            # display the help message for make-git-users
            parser.parse_known_args(text + ["--help"])

            sys.exit(0)

        # Run make-git-users
        arguments.execute(arguments)

        sys.exit(0)

    command_parser = registry.get_command(arguments.command)

    if not command_parser:
        print(
            'Command "{arguments.command}" was not found. Options were "{options}".'
            "".format(arguments=arguments, options=sorted(registry.get_command_keys()))
        )

        sys.exit(cli_constant.NO_COMMAND_FOUND)

    if needs_subparser_help:
        unknown_arguments = unknown_arguments + ["--help"]

    command_arguments = command_parser.parse_arguments(unknown_arguments)

    return arguments, command_arguments


@wrapping.run_once
def _register_plugins():
    for namespace in os.getenv("REZ_BATCH_PROCESS_PLUGINS", "").split(os.pathsep):
        namespace = namespace.strip()

        if not namespace:
            continue

        module = imports.import_nearest_module(namespace)

        if hasattr(module, "main"):
            module.main()


def main(text):
    """Run the main execution of the current script."""
    _register_plugins()

    arguments, command_arguments = parse_arguments(text)

    if arguments.verbose:
        _LOGGER.setLevel(logging.DEBUG)

    arguments.execute(arguments, command_arguments)
