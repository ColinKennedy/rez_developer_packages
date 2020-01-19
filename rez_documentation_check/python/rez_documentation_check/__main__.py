#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Check a Rez package for out of date intersphinx data."""

from __future__ import print_function

import argparse
import fnmatch
import json
import logging
import os
import pprint
import shutil
import sys
import tempfile

from python_compatibility.sphinx import conf_manager
from rez import exceptions as rez_exceptions
from rez import resolved_context
from rez.config import config
from rez_utilities import creator, inspection

from . import cli
from .core import check_constant, exceptions, python_dependency

_LOGGER = logging.getLogger(__name__)


def __check_for_intersphinx_mapping(arguments):
    """Find any report any missing intersphinx values.

    Args:
        arguments (:class:`argparse.Namespace`): The user-provided arguments from command-line.

    """
    try:
        source_package = _resolve_arguments(arguments)
    except EnvironmentError as error:
        print(error, file=sys.stderr)

        sys.exit(check_constant.NO_REZ_PACKAGE)

    _check_for_intersphinx_mapping(
        source_package,
        arguments.sphinx_files_must_exist,
        arguments.excluded_packages,
        allow_non_api=arguments.allow_non_api,
    )


def __fix_intersphinx_mapping(arguments):
    """Replace or add the ``intersphinx_mapping`` attribute to a user's conf.py Sphinx file.

    Args:
        arguments (:class:`argparse.Namespace`): The user-provided arguments from command-line.

    """
    source_package = _resolve_arguments(arguments)

    try:
        fix_applied = cli.fix_intersphinx_mapping(
            source_package,
            True,
            arguments.excluded_packages,
            allow_non_api=arguments.allow_non_api,
        )
    except exceptions.SphinxFileMissing as error:
        print(error, file=sys.stderr)

        sys.exit(check_constant.MISSING_SPHINX_FILE)

    if not fix_applied:
        print(
            "Everything looks good. All intersphinx mapping values exist. There's nothing to fix!"
        )

        sys.exit(check_constant.SUCCESS)

    print(
        'Fix was applied to Package "{source_package.name}" located at '
        '"{source_package.filepath}".'.format(source_package=source_package)
    )

    sys.exit(check_constant.SUCCESS)


def _delete(path):
    """Delete the given file or folder.

    Args:
        package (:class:`rez.developer_package.DeveloperPackage`):
            The path on-disk to delete + its parent directories.

    """
    if os.path.isdir(path):
        shutil.rmtree(path)
    if os.path.isfile(path):
        os.remove(path)


def _make_absolute(items, package):
    """Change `items` from relative paths to absolute paths.

    Args:
        items (iter[str]):
            A collection of files or folders on-disk. These paths can be
            absolute or relative.
        package (:class:`rez.developer_package.DeveloperPackage`):
            The package that will be used to resolve any relative
            paths in `items` into absolute paths. This works because
            the package is A. assumed as already built and B. resolves
            against ``rez_documentation_check`` into an installed
            variant, which each item in `items` should be inside of.

    Raises:
        RuntimeError:
            If a string in `items` cannot be linked to a file or folder on-disk.

    Returns:
        set[str]: The absolute file(s)/folder(s) on-disk. Every path must exist.

    """

    def _get_package_root(package, package_paths):
        root = os.getenv(inspection.get_root_key(package.name), "")

        if root:
            return root

        context = resolved_context.ResolvedContext(
            ["{package.name}=={package.version}".format(package=package)],
            package_paths=package_paths,
        )

        environment = context.get_environ()

        return environment[inspection.get_root_key(package.name)]

    output = set()
    package_root = inspection.get_packages_path_from_package(package)
    package_paths = [package_root] + config.packages_path  # pylint: disable=no-member

    try:
        root = _get_package_root(package, package_paths)
    except rez_exceptions.PackageNotFoundError:
        _LOGGER.error('Package could not be found in paths "%s".', package_paths)

        raise

    for item in items:
        path = item

        if not os.path.isabs(path):
            path = os.path.normcase(os.path.join(root, path))

        if not os.path.exists(path):
            raise RuntimeError(
                'Item "{item}" resolved to "{path}" but this path does not exist.'.format(
                    item=item, path=path
                )
            )

        output.add(path)

    return output


def _check_for_intersphinx_mapping(  # pylint: disable=too-many-arguments
    package, sphinx_files_must_exist, excluded_packages, allow_non_api=False,
):
    """Replace or add the ``intersphinx_mapping`` attribute to a user's conf.py Sphinx file.

    Args:
        package (:class:`rez.developer_package.DeveloperPackage`):
            The Rez package to find intersphinx mapping details for.
        sphinx_files_must_exist (bool):
            If True and the "conf.py" file doesn't exist, raise an
            exception. If False and the file doesn't exist, still report
            the missing intersphinx links.
        excluded_packages (iter[str]):
            The names of Rez packages to ignore. If an intersphinx
            key/value pair matches any of the names given to this
            parameter, it will be ignored. This parameter supports glob
            matching.
        allow_non_api (bool, optional):
            If False, only "recognized" API documentation will be
            returned. If True, all types of Rez documentation will be
            searched. Basically, False "guesses" correct documentation.
            Default is False.

    """
    try:
        missing = cli.get_missing_intersphinx_mappings(
            package, sphinx_files_must_exist, allow_non_api=allow_non_api,
        )
    except exceptions.SphinxFileMissing:
        print(
            '--sphinx-files-must-exist is enabled but "{package.name}" has no conf.py file.'.format(
                package=package
            ),
            file=sys.stderr,
        )

        sys.exit(check_constant.MISSING_SPHINX_FILE)

    packages_to_exclude = [
        name
        for name, _ in missing.items()
        if any((fnmatch.fnmatch(name, pattern) for pattern in excluded_packages))
    ]

    if packages_to_exclude:
        print(
            'Packages "{packages_to_exclude}" will be ignored from the final output.'.format(
                packages_to_exclude=packages_to_exclude
            )
        )

    missing = {
        name: item for name, item in missing.items() if name not in packages_to_exclude
    }

    if missing:
        print("Missing intersphinx links were found.")
        print("Please add the mapping below to your Sphinx conf.py file.")
        print()

        print("intersphinx_mapping = " + pprint.pformat(missing, indent=4))

        sys.exit(check_constant.MISSING_INTERSPHINX_LINKS)

    print("Intersphinx is up to date.")
    print("All checks passed!")

    sys.exit(check_constant.SUCCESS)


def _resolve_arguments(arguments):
    """Change user-provided arguments into something that this Python package can use.

    Args:
        arguments (:class:`argparse.Namespace`): The user-provided arguments from command-line.

    Raises:
        EnvironmentError: If no Rez package could be found from the user's input.

    Returns:
        tuple[:class:`rez.developer_package.DeveloperPackage`, set[str], str]:
            - The "source (current) Rez package". This package will be
            modified if called by the "fix" command.
            - The files / folders within the user's temporary "build Rez package"
            - The temporary directory where the "build Rez package" is written to.

    """
    current_root = os.getcwd()
    path = arguments.package

    if not os.path.isabs(arguments.package):
        path = os.path.normcase(os.path.join(current_root, path))

    if os.path.isfile(path):
        _LOGGER.debug('Path "%s" must be a directory leading to a Rez package.', path)
        path = os.path.dirname(path)

    package = inspection.get_nearest_rez_package(path)

    if not package:
        raise EnvironmentError(
            'Path "{path}" is not inside of a Rez package version. '
            "Please CD into a Rez package and try again.".format(path=path)
        )

    return package


def _parse_arguments(text):
    """Read the user's input text as Python types.

    Args:
        text (list[str]):
            All user-provided arguments that were given at the time when
            ``rez_documentation_check`` was run. Uusally, this list is empty.

    Returns:
        :class:`argparse.Namespace`: The parsed user input.

    """

    def _add_items_argument(parser, add_sphinx_flag=False):
        parser.add_argument(
            "-p",
            "--package",
            default=os.getcwd(),
            help="The directory of the Rez package to "
            "get / set an existing intersphinx mapping from.",
        )

        if add_sphinx_flag:
            parser.add_argument(
                "-s",
                "--sphinx-files-must-exist",
                action="store_true",
                help="If this flag is enabled, the found Rez package must have "
                "Sphinx documentation defined. Otherwise, the command will fail early.",
            )

        parser.add_argument(
            "-e",
            "--excluded-packages",
            default=set(),
            nargs="*",
            help="Any dependency that is found is ignored if its name is added to this parameter.",
        )

        parser.add_argument(
            "-a",
            "--add-rez-requirements",
            action="store_true",
            help="If this flag is included, the Rez package's explicit requirements "
            "will be searched for documentation.",
        )

        parser.add_argument(
            "-n",
            "--non-api",
            action="store_true",
            dest="allow_non_api",
            help="rez-documentation-check only searches for API documentation by default. "
            "Add this flag to search for other types of documentation, too.",
        )

    parser = argparse.ArgumentParser(description="")

    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="If added, debug logging messages will be printed.",
    )

    commands = parser.add_subparsers(
        title="commands",
        description="The available actions of rez-documentation-check.",
        help="Run one of these commands to make rez-documentation-check do something.",
    )

    checker = commands.add_parser(
        "check", help="Print missing Rez package intersphinx links."
    )
    checker.set_defaults(execute=__check_for_intersphinx_mapping)
    _add_items_argument(checker, add_sphinx_flag=True)

    fixer = commands.add_parser(
        "fix",
        description='Automatically add intersphinx links to the project\'s "{name}" file.'.format(
            name=conf_manager.SETTINGS_FILE
        ),
    )
    fixer.set_defaults(execute=__fix_intersphinx_mapping)
    _add_items_argument(fixer)

    return parser.parse_args(text)


def main(text):
    """Run the main execution of the current script.

    Warning:
        This function changes ``rez_documentation_check`` log level.

    Args:
        text (list[str]): The user-provided command-line text.

    """
    arguments = _parse_arguments(text)

    if arguments.verbose:
        logger = logging.getLogger("rez_documentation_check")
        logger.setLevel(logging.DEBUG)

    arguments.execute(arguments)


if __name__ == "__main__":
    logging.basicConfig(stream=sys.stdout, level=logging.INFO)
    main(sys.argv[1:])
