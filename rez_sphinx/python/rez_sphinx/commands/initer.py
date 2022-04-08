"""The module which handles the :ref:`rez_sphinx init` command."""

import logging
import os
import traceback

from python_compatibility import wrapping
from rez_utilities import finder
from sphinx.cmd import quickstart

from ..core import (
    bootstrap,
    configuration,
    constant,
    doc_finder,
    exception,
    package_change,
    path_control,
    sphinx_helper,
)
from ..preferences import preference

_LOGGER = logging.getLogger(__name__)
_SOURCE_FOLDER_NAME = "source"


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
        entries (list[Entry]):
            All descriptions of files to make during :ref:`rez_sphinx init`.

    """
    sphinx = configuration.ConfPy.from_directory(root)
    master_index = sphinx.get_master_document_path()
    lines = []

    for entry in entries:
        entry.write(root)
        lines.append(entry.get_toctree_line())

    sphinx_helper.add_links_to_a_tree(lines, master_index)


def _run_sphinx_quickstart(directory, options=tuple()):
    """Run `sphinx-quickstart`_.

    Args:
        directory (str):
            The starting folder on-disk where newly created documentation files
            will live under. e.g. ``"{root}/documentation"``.
        options (list[str], optional):
            The arguments which are passed directly to `sphinx-quickstart`_.

    Raises:
        NoPackageFound:
            If ``directory`` isn't in a Rez package.
        SphinxExecutionError:
            If `sphinx-quickstart`_ failed midway during execution.
        RuntimeError:
            If for some reason `sphinx-quickstart`_ completed but
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

    source = doc_finder.get_source_from_directory(os.path.dirname(directory))
    path = os.path.join(source, constant.SPHINX_CONF_NAME)

    if not os.path.isfile(path):
        raise RuntimeError(
            'Something went wrong, "{path}" was not defined.'.format(path=path)
        )

    return path


def init(package, quick_start_options=tuple()):
    """Connect the Rez package at ``directory`` to :ref:`rez_sphinx`.

    Warning:
        This function generates many files directly underneath
        ``directory`` as well as changes your source Rez package.py
        file.  Save your work first before running this function!

    Args:
        package (rez.packages.Package):
            The Rez package to apply documentation onto.
        quick_start_options (list[str], optional):
            User-provided arguments to consider while resolving
            `sphinx-quickstart`_ values.

    """
    initial_files = preference.get_initial_files_from_configuration()

    options = preference.get_quick_start_options(package, options=quick_start_options)

    root = finder.get_package_root(package)
    folder_name = preference.get_documentation_root_name(package=package)

    if preference.SPHINX_SEPARATE_SOURCE_AND_BUILD in options:
        documentation_source_root = os.path.join(root, folder_name, _SOURCE_FOLDER_NAME)
    else:
        documentation_source_root = os.path.join(root, folder_name)

    with wrapping.silence_printing():
        if preference.SPHINX_SEPARATE_SOURCE_AND_BUILD in options:
            quickstart_root = os.path.dirname(documentation_source_root)
        else:
            quickstart_root = documentation_source_root

        configuration_path = _run_sphinx_quickstart(quickstart_root, options=options)

    if preference.SPHINX_SEPARATE_SOURCE_AND_BUILD in options:
        _add_initial_files(documentation_source_root, initial_files)
        _add_build_directory(os.path.dirname(documentation_source_root))
    else:
        _add_initial_files(documentation_source_root, initial_files)

    bootstrap.append_bootstrap_lines(configuration_path)

    package_change.initialize_rez_package(package)
