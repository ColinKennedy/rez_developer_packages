"""A companion module to :mod:`api_builder` which builds the API .rst files."""

import io
import logging
import os
import sys
import textwrap
import traceback

from python_compatibility import filer
from rez_utilities import finder
from sphinx.ext import apidoc

from ..preferences import preference
from . import configuration, exception, generic, path_control, sphinx_helper

_LOGGER = logging.getLogger(__name__)
_CURRENT_DIRECTORY = os.path.dirname(os.path.realpath(__file__))
_PACKAGE_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(_CURRENT_DIRECTORY)))
_TEMPLATES_DIRECTORY = os.path.join(_PACKAGE_ROOT, "templates")
_TEMPLATE_DIR_LONG_FLAG = "--templatedir"
_TEMPLATE_DIR_SHORT_FLAG = "-t"


def _add_disclaimer_readme(directory):
    """Add a README file for API documentation into ``directory``.

    Args:
        directory (str):
            The folder where API documentation + disclaimer must be placed.
            e.g. ``"{root}/documentation/source/api"``.

    """
    with io.open(os.path.join(directory, "README"), "w", encoding="utf-8") as handler:
        handler.write(
            generic.decode(
                textwrap.dedent(
                    """\
                    This directory and its contents are auto-generated and ignored
                    by git. Do not place any files here that you wish to keep!"""
                )
            )
        )


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
    _add_disclaimer_readme(api_directory)

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
        options (list[str], optional):
            User-provided arguments to add into the `sphinx-apidoc`_ command.

    Raises:
        NoPackageFound:
            If ``directory`` isn't in a Rez package.
        EnvironmentError:
            If the user needs the default "templates" directory but it is missing.
        NoPythonFiles:
            If no Python files exist then no API .rst files can be built.
            So this function raises this exception, exiting early.
        SphinxExecutionError:
            If running `sphinx-apidoc`_ failed midway and could not complete.

    Returns:
        bool:
            If there wasn't any Python file to generate API documentation for,
            return False.

    """
    install_package = finder.get_nearest_rez_package(directory)

    if not install_package:
        raise exception.NoPackageFound(
            'Directory "{directory}" is not inside an installed Rez package.'.format(
                directory=directory
            )
        )

    install_directory = path_control.get_installed_root(install_package.name)

    sources = _get_python_source_roots(install_directory)

    if not sources:
        _LOGGER.warning(
            'Install directory "%s" has no Python files. '
            "Did your Rez package install Python files correctly?",
            install_directory,
        )

        return False

    allow_custom_templates = (
        _TEMPLATE_DIR_SHORT_FLAG not in options
        and _TEMPLATE_DIR_LONG_FLAG not in options
        and preference.allow_apidoc_templates(package=install_package)
    )

    if allow_custom_templates and not os.path.isdir(_TEMPLATES_DIRECTORY):
        raise EnvironmentError(
            'Directory "{_TEMPLATES_DIRECTORY}" does not exist.'.format(
                _TEMPLATES_DIRECTORY=_TEMPLATES_DIRECTORY
            )
        )

    for python_source_root in sources:
        command = [python_source_root, "--output-dir", destination]

        if allow_custom_templates and sphinx_helper.supports_apidoc_templates():
            command.extend([_TEMPLATE_DIR_LONG_FLAG, _TEMPLATES_DIRECTORY])

        command.extend(options)
        _LOGGER.debug('Generating API documentation using "%s" command.', command)

        try:
            apidoc.main(command)
        except SystemExit:
            _LOGGER.warning(
                'sphinx-apidoc failed to run. Rolling back the changes in "%s" folder.',
                destination,
            )

            path_control.clear_directory(destination)

            raise exception.SphinxExecutionError(
                "sphinx-apidoc failed to run. See the help, below:\n\n{help_}".format(
                    help_=apidoc.get_parser().format_help()
                )
            )

    return True


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

    return {path for path in sys.path if filer.in_directory(path, root, follow=False)}


def _update_master_file(directory):
    """Add the newly-created API entry "modules.rst" file to the master `toctree`_.

    Args:
        directory (str):
            The absolute path to the documentation source directory,
            within some source Rez package.

    Raises:
        NoPackageFound:
            If ``directory`` isn't inside of a source Rez package with
            documentation.

    """
    sphinx = configuration.ConfPy.from_directory(directory)
    path = sphinx.get_master_document_path()
    package = finder.get_nearest_rez_package(directory)

    if not package:
        raise exception.NoPackageFound(
            'Directory "{directory}" is not inside of a source Rez package.'.format(
                directory=directory
            )
        )

    toctree_line = preference.get_master_api_documentation_line(package=package)
    sphinx_helper.add_links_to_a_tree([toctree_line], path)


def generate_api_files(directory, options=tuple()):
    """Create the "api" folder for :ref:`rez_sphinx build run`.

    This is a bit confusing but :ref:`rez_sphinx build run` uses the user's
    **installed** Python files in order to generate an "api" directory in the
    user's **source** Rez package.

    - Create the "api" folder
    - Fill it with auto-generated .rst files
    - Update the master index.rst with a reference to the auto-generated
      "api/modules.rst" file, if it isn't already there.

    Args:
        directory (str):
            The absolute path to the documentation source directory,
            within some Rez package.
        options (container[str], optional):
            All arguments to pass directly to `sphinx-apidoc`_.

    """
    api_directory = _clear_api_directory(directory)
    generated = _generate_api_files(directory, api_directory, options=options)

    if generated:
        _update_master_file(directory)
