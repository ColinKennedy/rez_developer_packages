"""The module which handles the :ref:`rez_sphinx build run` command."""

import os
import traceback

from rez.config import config
from rez_utilities import finder
from sphinx.cmd import build as sphinx_build

from ...core import api_builder, doc_finder, exception, sphinx_helper
from ...preferences import preference


def _get_documentation_build(source):
    """Find the directory where documentation must be built into.

    Args:
        source (str):
            The parent directory of `Sphinx conf.py <conf.py>`_.

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
    build_directory = os.path.join(  # Usually {rez_root}/build
        root,
        config.build_directory,  # pylint: disable=no-member
    )

    return os.path.join(  # {rez_root}/build/documentation
        build_directory, preference.get_documentation_root_name()
    )


def _get_documentation_source(root):
    """Find the directory which contains `Sphinx conf.py`_ or fail trying.

    Args:
        root (str):
            A directory on-disk to search within for the `Sphinx conf.py <conf.py>`_.

    Raises:
        NoDocumentationFound:
            If ``root`` needs to initialize some documentation.

    Returns:
        str: The parent directory of `Sphinx conf.py <conf.py>`_.

    """
    try:
        configuration = sphinx_helper.find_configuration_path(root)
    except RuntimeError:
        raise exception.NoDocumentationFound(
            'Directory "{root}" has no documentation. '
            "Run `rez_sphinx init` to fix this."
        )

    return os.path.dirname(configuration)


def _validate_non_default_files(directory):
    """Check if ``directory`` has non-default documentation.

    Args:
        directory (str):
            The documentation source root to look within for expected files.
            If a file is found, it must have hand-written documentation applied
            or it is rejected.

    Raises:
        NoDocumentationWritten:
            If any default, known file was never changed by the user.

    """
    invalids = set()

    for entry in preference.get_init_default_entries():
        full = os.path.join(directory, entry.get_relative_path())

        if not os.path.isfile(full):
            continue

        with open(full, "r") as handler:
            data = handler.read()

        if data == entry.get_default_text():
            invalids.add(full)

    if not invalids:
        return

    raise exception.NoDocumentationWritten(
        'Paths "{invalids}" have no hand-written documentation. '
        "Please add some documentation here!".format(
            invalids=", ".join(sorted(invalids)),
        )
    )


def build(
    directory,
    api_mode=api_builder.FULL_AUTO.label,
    api_options=tuple(),
    no_api_doc=False,
):
    """Generate .html files from the Sphinx documentation in ``directory``.

    Args:
        directory (str):
            The absolute path to a root Rez package.
        api_mode (str, optional):
            A description of what to do about Python API documentation.
            For example, should it be generated or not? See
            :mod:`.api_builder` for details.
        api_options (list[str], optional):
            User-provided arguments to pass to `sphinx-apidoc`_.
        no_api_doc (bool, optional):
            If True, don't build any API documentation. If False, API .rst
            files will be auto-generated just before `sphinx-build`_ is ran.

    Raises:
        NoPackageFound:
            If ``directory`` is invalid.
        SphinxExecutionError:
            If `sphinx-build`_ failed midway before it could be completed.

    """
    package = finder.get_nearest_rez_package(directory)

    if not package:
        raise exception.NoPackageFound(
            'Directory "{directory}" is not in a Rez package.'.format(
                directory=directory
            )
        )

    try:
        source_directory = doc_finder.get_source_from_package(package)
    except RuntimeError:
        raise exception.NoDocumentationFound(
            'Directory "{root}" has no documentation. '
            "Run `rez_sphinx init` to fix this."
        )

    if preference.check_default_files():
        _validate_non_default_files(source_directory)

    api_options = preference.get_api_options(options=api_options)

    # TODO : This doesn't take into account split builds (it needs to fall back
    # to the Rez build folder if the user doesn't have a documentation/source
    # folder
    #
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

    if not no_api_doc and preference.is_api_enabled() and api_mode.execute:
        api_mode.execute(source_directory, options=api_options)

    try:
        sphinx_build.main(parts)
    except SystemExit:
        text = "".join(traceback.format_exc())

        raise exception.SphinxExecutionError(text)
