"""The module which handles the :ref:`rez_sphinx build` command."""

import os
import traceback

from rez.config import config
from rez_utilities import finder
from sphinx.cmd import build as sphinx_build

from ..preferences import preference
from ..core import api_builder, exception, sphinx_helper


def _get_documentation_build(source):
    """Find the directory where documentation must be built into.

    Args:
        source (str):
            The parent directory of :ref:`Sphinx conf.py <conf.py>`.

    Returns:
        str:
            The found path on-disk where documentation must be
            built. This path does not need to exist (yet).

    """
    separate_build_folder = os.path.join(os.path.dirname(source), "build")

    if os.path.isdir(separate_build_folder):
        # Most :ref:`rez_sphinx` configurations will use this path
        return separate_build_folder  # {rez_root}/documentation/build

    package = finder.get_nearest_rez_package(source)
    root = finder.get_package_root(package)
    build_directory = os.path.join(  # {rez_root}/build
        root,  # {rez_root}
        config.build_directory,  # build (default name)
    )

    return os.path.join(  # {rez_root}/build/documentation
        build_directory, "documentation"
    )


def _get_documentation_source(root):
    """Find the directory which contains :ref:`Sphinx conf.py` or fail trying.

    Args:
        root (str):
            A directory on-disk to search within for the
            :ref:`Sphinx conf.py <conf.py>`.

    Raises:
        :class:`.NoDocumentationFound`:
            If ``root`` needs to initialize some documentation.

    Returns:
        str: The parent directory of :ref:`Sphinx conf.py <conf.py>`.

    """
    try:
        configuration = sphinx_helper.find_configuration_path(root)
    except RuntimeError:
        raise exception.NoDocumentationFound(
            'Directory "{root}" has no documentation. '
            "Run `rez_sphinx init` to fix this."
        )

    return os.path.dirname(configuration)


def build(directory, api_mode=api_builder.FULL_AUTO.label, api_options=tuple()):
    """Generate .html files from the Sphinx documentation in ``directory``.

    Args:
        directory (str):
            The absolute path to a root Rez package.
        api_mode (str, optional):
            A description of what to do about Python API documentation.
            For example, should it be generated or not? See
            :mod:`api_builder` for details.
        api_options (list[str], optional):
            User-provided arguments to pass to :ref:`sphinx-apidoc`.

    Raises:
        :class:`.NoPackageFound`:
            If ``directory`` is invalid.
        :class:`.SphinxExecutionError`:
            If :ref:`sphinx-build` failed midway before it could be completed.

    """
    package = finder.get_nearest_rez_package(directory)

    if not package:
        raise exception.NoPackageFound(
            'Directory "{directory}" is not in a Rez package.'.format(
                directory=directory
            )
        )

    api_options = preference.get_api_options(options=api_options)

    source_directory = _get_documentation_source(directory)
    build_directory = _get_documentation_build(source_directory)

    parts = [
        "-b",
        "html",  # Always assume .html output
        source_directory,
        build_directory,
    ]

    if not os.path.isdir(build_directory):
        os.makedirs(build_directory)

    api_mode = api_builder.get_from_label(api_mode)

    if api_mode != api_builder.GENERATE and api_mode.execute:
        # Skip ``GENERATE`` because it would've already ran during
        # ``rez_sphinx init``.
        #
        api_mode.execute(source_directory, options=api_options)

    try:
        sphinx_build.main(parts)
    except SystemExit:
        text = "".join(traceback.format_exc())

        raise exception.SphinxExecutionError(text)
