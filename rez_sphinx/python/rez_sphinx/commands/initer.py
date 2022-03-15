"""The module which handles the :doc:`init_command` command."""

import logging
import os
import traceback

from python_compatibility import wrapping
from sphinx.cmd import quickstart

from ..core import (
    bootstrap,
    configuration,
    exception,
    package_change,
    path_control,
    sphinx_helper,
)
from ..preferences import preference

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


def _add_initial_files(root, entries):
    """Add template documentation files to ``root``, based on ``configuration``.

    "Template documentation files" in this case just refers to "A common set of
    .rst files which users are expected to fill out by hand". Examples could
    include "Developer Documentation", "User Documentation", etc.

    Args:
        root (str):
            The directory on-disk where the source documentation lives. e.g.
            {rez_root}/documentation/source is the most common path.
        entries (list[:class:`.Entry`]):
            All descriptions of files to make during :doc:`init_command`.

    """
    sphinx = configuration.ConfPy.from_directory(root)
    master_index = sphinx.get_master_document_path()
    lines = []

    for entry in entries:
        full = os.path.join(root, entry.get_relative_path())
        directory = os.path.dirname(full)

        if not os.path.isdir(directory):
            os.makedirs(directory)

        with open(full, "w") as handler:
            handler.write(entry.get_default_text())

        lines.append(entry.get_toctree_line())

    sphinx_helper.add_links_to_a_tree(lines, master_index)


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
            The starting folder on-disk where newly created documentation files
            will live under. e.g. "{rez_root}/documentation"
        quick_start_options (list[str], optional):
            User-provided arguments to consider while resolving
            :ref:`sphinx-quickstart` values.

    """
    # TODO : Need to add API documentation support here.
    # Or get it from rez-config settings
    #
    initial_files = preference.get_initial_files_from_configuration()

    options = preference.get_quick_start_options(
        package.name, options=quick_start_options
    )

    with wrapping.silence_printing():
        configuration_path = _run_sphinx_quickstart(directory, options=options)

    if preference.SPHINX_SEPARATE_SOURCE_AND_BUILD in options:
        # TODO : Check if "source" can be some variable instead of hard-coded
        _add_initial_files(os.path.join(directory, "source"), initial_files)
        _add_build_directory(directory)
    else:
        _add_initial_files(directory, initial_files)

    bootstrap.append_bootstrap_lines(configuration_path)

    package_change.initialize_rez_package(package)
