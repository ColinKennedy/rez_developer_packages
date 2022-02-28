"""A companion module to :mod:`api_builder` which builds the API .rst files."""

import logging
import os
import sys
import traceback

from python_compatibility import filer
from rez_utilities import finder
from sphinx.ext import apidoc

from . import path_control

_LOGGER = logging.getLogger(__name__)


def _get_python_source_roots(directory):
    """Find every directory on-disk where ``directory`` contains Python files.

    Args:
        directory (str):
            The absolute path to a folder on-disk where either A. An
            installed Rez package exists ot B. A source Rez package
            (which is already installed someplace else). In either
            case, this found package must be part of the user's current
            runtime resolve environment or this function will return
            nothing.

    Raises:
        RuntimeError: If ``directory`` has no Rez package.

    Returns:
        set[str]:
            The directory containing all Python files which the Rez
            package in ``directory`` defines.

    """
    package = finder.get_nearest_rez_package(directory)

    if not package:
        raise RuntimeError(
            'Directory "{directory}" is not inside a Rez package.'.format(
                directory=directory
            )
        )

    root = finder.get_package_root(package)

    return {path for path in sys.path if filer.in_directory(path, root)}


def generate_api_files(directory, options=tuple()):
    """Create the "api" folder so :ref:`rez_sphinx build` includes the user's Python files.

    Args:
        directory (str):
            The absolute path to a folder on disk. This folder should be
            a sub-folder inside of a Rez package to the root of the Rez package.
        options (container[str], optional):
            All arguments to pass directly to :ref:`sphinx-apidoc`.

    Raises:
        :class:`.SphinxExecutionError`:
            If :ref:`sphinx-apidoc` fails midway before it could finish.

    """
    api_directory = os.path.join(directory, "api")

    if not os.path.isdir(api_directory):
        os.makedirs(api_directory)

    path_control.clear_directory(api_directory)
    path_control.add_gitignore(api_directory)

    package = finder.get_nearest_rez_package(directory)
    install_directory = path_control.get_installed_root(package.name)

    for python_source_root in _get_python_source_roots(install_directory):
        command = [python_source_root, "--output-dir", api_directory]
        command.extend(options)

        try:
            # TODO : Double check that this doesn't use $PWD at all
            apidoc.main(command)
        except SystemExit:
            _LOGGER.warning(
                'sphinx-apidoc failed to run. Rolling back the changes in "%s" folder.',
                api_directory,
            )

            path_control.clear_directory(api_directory)

            text = "".join(traceback.format_exc())

            raise SphinxExecutionError(text)
