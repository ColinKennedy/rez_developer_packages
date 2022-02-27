"""The module which handles the :ref:`rez_sphinx init` command."""

import logging
import os
import textwrap

from sphinx.cmd import quickstart

from ..core import (bootstrap, exception, package_change, path_control, preference,
                    sphinx_helper)

_LOGGER = logging.getLogger(__name__)


def _add_build_directory(directory):
    """Add a "build" folder under ``directory``.

    Args:
        directory (str):
            The absolute path to the root documentation folder. Usually
            this is "{rez_root}/documentation"

    """
    build = os.path.join(directory, "build")

    if not os.path.isdir(build):
        os.makedirs(build)

    path_control.add_gitignore(build)


def _run_sphinx_quickstart(directory, options=tuple()):
    """Run :ref:`sphinx-quickstart`.

    Args:
        directory (str):
            The starting folder on-disk where newly created
            documentation files will live under.
        options (list[str], optional):
            The arguments which are passed directly to :ref:`sphinx-quickstart`.

    Raises:
        :class:`.SphinxExecutionError`:
            If :ref:`sphinx-quickstart` failed midway during execution.
        RuntimeError:
            If for some reason :ref:`sphinx-quickstart` completed but
            somehow failed to generate the expected files.

    """
    options = options or []
    arguments = [directory] + options

    _LOGGER.debug('Got sphinx-quickstart arguments "%s".', arguments)
    _LOGGER.info('Now running sphinx-quickstart in "%s" folder.', directory)

    try:
        quickstart.main(arguments)
    except SystemExit:
        text = "".join(traceback.format_exc())

        raise exception.SphinxExecutionError(text)

    path = sphinx_helper.find_configuration_path(directory)

    if not os.path.isfile(path):
        raise RuntimeError(
            'Something went wrong, "{path}" was not defined.'.format(path=path)
        )

    return path


def init(package, directory, quick_start_options=tuple()):
    """Connect the Rez package at ``directory`` to :ref:`rez_sphinx`.

    Warning:
        This function generates many files directly underneath
        ``directory`` as well as changes your source Rez package.py
        file.  Save your work first before running this function!

    Args:
        package (:class:`rez.developer_package.DeveloperPackage`):
            The Rez package to apply documentation onto.
        directory (str):
            The starting folder on-disk where newly created
            documentation files will live under.
        quick_start_options (list[str], optional):
            User-provided arguments to consider while resolving
            :ref:`sphinx-quickstart` values.

    """
    # TODO : Need to add API documentation support here. Or get it from rez-config settings
    options = preference.get_quick_start_options(options=quick_start_options)
    configuration_path = _run_sphinx_quickstart(directory, options=options)

    if preference.SPHINX_SEPARATE_SOURCE_AND_BUILD in options:
        _add_build_directory(directory)

    bootstrap.append_bootstrap_lines(configuration_path)

    package_change.initialize_rez_package(package)
