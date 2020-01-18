#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The main module that makes ``sphinx_apidoc_check`` work.

It handles gathering the user's input arguments and running the
``sphinx-apidoc`` Python calls to find out which .rst files need to be
generated.

"""

from __future__ import print_function

import glob
import os
import sys

from python_compatibility import wrapping
from sphinx.ext import apidoc

from .core import apidoc_patcher, check_exception


def _get_apidoc_main_function():
    """callable[list[str]] -> int: The function that is used to print the .rst files to create."""
    return apidoc.main


def _get_sphinx_apidoc_arguments(text):
    """Change some raw shell input text into valid Python objects.

    Args:
        text (list[str]):
            The arguments to pass directly into ``sphinx-apidoc``.
            e.g. ["python", "--output-dir", "documentation/source/api"].

    Raises:
        :class:`.InvalidSphinxArguments`:
            If the given `text` cannot be parsed by ``sphinx-apidoc``.

    Returns:
        :class:`argparse.Namespace`: The parsed user input.

    """
    parser = apidoc.get_parser()

    try:
        with wrapping.capture_pipes() as output:
            return parser.parse_args(text)
    except SystemExit as error:
        _, stderr = output

        if error.code != 2:
            print("Found issue:", file=sys.stderr)
            print(stderr, file=sys.stderr)

            raise

        stderr = stderr.replace("__main__.py", "sphinx-apidoc")
        stderr = stderr.splitlines()[-1]  # The first line shows the exact usage

        raise check_exception.InvalidSphinxArguments(
            'Command "{text}" is not a valid call to ``sphinx-apidoc``. '
            'Here\'s the full error message "{stderr}".'.format(
                text=" ".join(text), stderr=stderr.strip()
            )
        )


def check(text, directory=""):
    """Look for Sphinx API documentation .rst files that need to be created.

    Args:
        text (list[str]):
            The user's raw input options. These will be parsed into
            options and used to control the execution of this function.
            e.g. ['"python --output-dir documentation/source/api"', "--no-strict"].
        directory (str, optional):
            The folder that will be cd'ed into while the
            ``sphinx-apidoc`` main function is running.

    Raises:
        :class:`.DirectoryDoesNotExist`: If the given `directory` is not a folder on-disk.
        :class:`.NoDryRun`: If the user does not include the "--dry-run" flag in `text`.
        RuntimeError: If for whatever reason ``sphinx-apidoc`` fails to run.

    Returns:
        tuple[set[str], set[str], set[str]]:
            The files of file paths that would be created by the
            ``sphinx-apidoc`` command, the files that would remain
            unchanged, and the files in that currently exist in the
            destination folder that do not point to any Python modules
            (and should be removed).

    """
    if not directory:
        directory = os.getcwd()

    if not os.path.isabs(directory):
        directory = os.path.normcase(os.path.join(os.getcwd(), directory))

    if not os.path.isdir(directory):
        raise check_exception.DirectoryDoesNotExist(
            'Path "{directory}" is not a directory. Check your spelling and try again.'.format(
                directory=directory
            ),
        )

    arguments = _get_sphinx_apidoc_arguments(text)

    if not arguments.dryrun:
        raise check_exception.NoDryRun(
            'Command "{text}" must have --dry-run in its arguments'.format(text=text)
        )

    with wrapping.keep_cwd(directory):
        os.chdir(directory)

        with wrapping.capture_pipes() as output:
            function = _get_apidoc_main_function()
            function(text)

        stdout, stderr = output

    if stderr:
        raise RuntimeError(
            'Input "{text}" caused sphinx-apidoc to fail while running.'.format(
                text=text
            )
        )

    files_that_sphinx_sees = apidoc_patcher.parse(stdout.strip())
    existing_files = set(glob.glob(os.path.join(arguments.destdir, "*")))

    files_to_skip = existing_files.intersection(files_that_sphinx_sees)
    files_to_add = files_that_sphinx_sees - files_to_skip
    files_to_remove = existing_files - files_to_add - files_to_skip

    return (files_to_add, files_to_skip, files_to_remove)
