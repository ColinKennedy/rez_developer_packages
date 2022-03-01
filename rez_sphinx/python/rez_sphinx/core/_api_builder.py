"""A companion module to :mod:`api_builder` which builds the API .rst files."""

import logging
import os
import sys
import traceback
import textwrap

from python_compatibility import filer
from rez_utilities import finder
from sphinx.ext import apidoc

from . import configuration, exception, path_control, preference, sphinx_helper

_LOGGER = logging.getLogger(__name__)
_MISSING_TOCTREE_TEMPLATE = textwrap.dedent(
    """\
    .. toctree::
        :max-depth: 1

        {toctree_line}
    """
)


def _add_api_link_to_a_tree(toctree_line, trees, data):
    """Find the appropriate :ref:`toctree` to add ``line`` onto.

    Args:
        toctree_line (str): The API documentation line to append.
        trees (list[list[str]]): Each found toctree.
        data (str): The blob of text which ``trees`` are a part of.

    Raises:
        RuntimeError: If ``trees`` already contains ``toctree_line`` at least once.

    Returns:
        str: The newly modified ``data``, which now includes ``line``.

    """
    for tree in trees:
        for line in tree:
            if line == toctree_line:
                _LOGGER.debug(
                    'API documentation already added in tree "%s". Skipping.',
                    tree,
                )

                raise RuntimeError("API link already exists.")

    tree = trees[0]
    _, end_line, _ = tree

    lines = data.splitlines()
    indent = sphinx_helper.get_toctree_indent(lines)

    if sphinx_helper.is_empty_toctree(lines):
        end_line += 1

    lines.insert(end_line, indent + toctree_line)

    return "\n".join(lines)


def _clear_api_directory(directory):
    """Delete the contents of the "api" directory and re-make it.

    Args:
        directory (str):
            The root source documentation folder. Usually it's
            "{source_rez_root}/documentation/source".

    """
    api_directory = os.path.join(directory, "api")

    if not os.path.isdir(api_directory):
        os.makedirs(api_directory)

    path_control.clear_directory(api_directory)
    path_control.add_gitignore(api_directory)

    return api_directory


def _generate_api_files(directory, destination, options=tuple()):
    """Fill ``destination`` source documentation with with auto-generated .rst files.

    Args:
        directory (str):
            The absolute path to the documentation source directory,
            within some source Rez package.
        destination (str):
            The exact folder where source API .rst files will go
            into. Usually this is "{source_rez_root}/documentation/source/api".

    Raises:
        :class:`.NoPythonFiles`:
            If no Python files exist then no API .rst files can be built.
            So this function raises this exception, exiting early.
        :class:`.SphinxExecutionError`:
            If running :ref:`sphinx-apidoc` failed midway and could not complete.

    """
    install_package = finder.get_nearest_rez_package(directory)
    install_directory = path_control.get_installed_root(install_package.name)

    sources = _get_python_source_roots(install_directory)

    if not sources:
        raise exception.NoPythonFiles(
            'Install directory "{install_directory}" has no Python files. '
            "Did your Rez package install Python files correctly?".format(
                install_directory=install_directory
            )
        )

    for python_source_root in sources:
        command = [python_source_root, "--output-dir", destination]
        command.extend(options)

        try:
            # TODO : Double check that this doesn't use $PWD at all
            apidoc.main(command)
        except SystemExit:
            _LOGGER.warning(
                'sphinx-apidoc failed to run. Rolling back the changes in "%s" folder.',
                destination,
            )

            path_control.clear_directory(destination)

            text = "".join(traceback.format_exc())

            raise exception.SphinxExecutionError(text)


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


def _update_master_file(directory):
    """Add the newly-created API entry "modules.rst" file to the master :ref:`toctree`.

    Args:
        directory (str):
            The absolute path to the documentation source directory,
            within some source Rez package.

    """
    sphinx = configuration.ConfPy.from_path(os.path.join(directory, "conf.py"))
    path = os.path.join(directory, sphinx.get_master_document_name())
    toctree_line = preference.get_master_api_documentation_line()

    with open(path, "r") as handler:
        data = handler.read()

    trees = sphinx_helper.get_toctrees(data)

    if trees:
        try:
            new_data = _add_api_link_to_a_tree(toctree_line, trees, data)
        except RuntimeError:
            return
    else:
        new_data = data + _MISSING_TOCTREE_TEMPLATE.format(toctree_line=toctree_line)

    with open(path, "w") as handler:
        handler.write(new_data)


def generate_api_files(directory, options=tuple()):
    """Create the "api" folder so :ref:`rez_sphinx build` uses the user's Python files.

    - Create the "api" folder
    - Fill it with auto-generated .rst files
    - Update the master index.rst with a reference to the auto-generated
      "api/modules.rst" file, if it isn't already there.

    Args:
        directory (str):
            The absolute path to the documentation source directory,
            within some Rez package.
        options (container[str], optional):
            All arguments to pass directly to :ref:`sphinx-apidoc`.

    """
    api_directory = _clear_api_directory(directory)
    _generate_api_files(directory, api_directory, options=options)
    _update_master_file(directory)
