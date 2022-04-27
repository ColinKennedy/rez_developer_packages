"""The module which handles the :ref:`rez_sphinx init` command."""

import logging
import os

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


def _check_for_existing_documentation(directory):
    """Fail if ``directory`` already has source documentation.

    Args:
        directory (str): The root directory of your source Rez package.

    Raises:
        RezSphinxException: If documentation already exists.

    """
    try:
        doc_finder.get_source_from_directory(directory)
    except RuntimeError:
        # The package directory doesn't have documentation exists. Just ignore it.
        return

    raise exception.RezSphinxException(
        'Directory "{directory}" already has documentation.'.format(directory=directory)
    )


def _run_raw_sphinx_quickstart(arguments):
    """Call `sphinx-quickstart`_ as if it were from the terminal, using ``arguments``.

    Args:
        arguments (list[str]):
            The exact arguments to pass to `sphinx-quickstart`_, e.g. ``sys.argv[1:]``.

    Raises:
        SphinxExecutionError: If the commands fails, for any reason.

    """
    quickstart_error = quickstart.main(arguments)

    if not quickstart_error:
        return

    raise exception.SphinxExecutionError(
        'sphinx-quickstart failed to run. Got error code "{quickstart_error}". '
        "See help below for details\n\n{help_}".format(
            quickstart_error=quickstart_error,
            help_=quickstart.get_parser().format_help(),
        )
    )


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

    _run_raw_sphinx_quickstart(arguments)

    source = doc_finder.get_source_from_directory(os.path.dirname(directory))
    path = os.path.join(source, constant.SPHINX_CONF_NAME)

    if os.path.isfile(path):
        return path

    raise RuntimeError(
        'Something went wrong, "{path}" was not defined.'.format(path=path)
    )


def init(package, quick_start_options=tuple(), skip_existing=False, verbose=False):
    """Connect a Rez source ``package`` to :ref:`rez_sphinx`.

    Warning:
        This function generates many files directly underneath
        ``package`` as well as changes your source Rez package.py
        file. Save your work first before running this function!

    Args:
        package (rez.packages.Package):
            The Rez package to apply documentation onto.
        quick_start_options (list[str], optional):
            User-provided arguments to consider while resolving
            `sphinx-quickstart`_ values.
        skip_existing (bool, optional):
            If False, check for documentation and error if existing
            documentation is found. If True, instead of erroring, do nothing
            and return early.
        verbose (bool, optional):
            If True, show `sphinx-quickstart`_ output.

    """
    initial_files = preference.get_initial_files_from_configuration()

    options = preference.get_quick_start_options(package, options=quick_start_options)

    root = finder.get_package_root(package)
    folder_name = preference.get_documentation_root_name(package=package)

    if preference.SPHINX_SEPARATE_SOURCE_AND_BUILD in options:
        documentation_source_root = os.path.join(
            root,
            folder_name,
            constant.SOURCE_FOLDER_NAME,
        )
    else:
        documentation_source_root = os.path.join(root, folder_name)

    if preference.SPHINX_SEPARATE_SOURCE_AND_BUILD in options:
        quickstart_root = os.path.dirname(documentation_source_root)
    else:
        quickstart_root = documentation_source_root

    try:
        _check_for_existing_documentation(os.path.dirname(quickstart_root))
    except exception.RezSphinxException:
        if not skip_existing:
            raise

        _LOGGER.info(
            'Directory "%s" already has documentation. Skipping.',
            documentation_source_root,
        )

        return

    if verbose:
        configuration_path = _run_sphinx_quickstart(quickstart_root, options=options)
    else:
        with wrapping.silence_printing():
            configuration_path = _run_sphinx_quickstart(
                quickstart_root, options=options
            )

    if preference.SPHINX_SEPARATE_SOURCE_AND_BUILD in options:
        _add_initial_files(documentation_source_root, initial_files)
        _add_build_directory(os.path.dirname(documentation_source_root))
    else:
        _add_initial_files(documentation_source_root, initial_files)

    bootstrap.append_bootstrap_lines(configuration_path)

    package_change.initialize_rez_package(package)
