"""The module which handles the :ref:`rez_sphinx build run` command."""

import io
import logging
import os
import shutil
import traceback

from rez.config import config
from rez_utilities import finder
from sphinx.cmd import build as sphinx_build

from ...core import api_builder, doc_finder, exception
from ...preferences import preference

_LOGGER = logging.getLogger(__name__)


def _clear_directory(directory):
    """Delete all contents in ``directory`` without removing ``directory``, itself.

    Args:
        directory (str): An absolute or relative path to a folder on-disk.

    """
    for name in os.listdir(directory):
        full = os.path.join(directory, name)

        if os.path.isdir(full):
            shutil.rmtree(full)
        elif os.path.islink(full):
            os.unlink(full)
        elif os.path.isfile(full):
            os.remove(full)


def _get_name(path):
    """str: Get the parent directory name of ``name``."""
    return os.path.basename(os.path.dirname(path))


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
        if not entry.check_pre_build():
            _LOGGER.debug('Skipping "%s" because it is ignored during build.', entry)

            continue

        full = os.path.join(directory, entry.get_relative_path())

        if not os.path.isfile(full):
            continue

        with io.open(full, "r", encoding="utf-8") as handler:
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


def get_documentation_build(source):
    """Find the directory where documentation must be built into.

    Args:
        source (str): The parent directory of `Sphinx conf.py`_.

    Raises:
        RuntimeError: If ``source`` was queried but it isn't in a Rez package.

    Returns:
        str:
            The found path on-disk where documentation must be
            built. This path does not need to exist (yet).

    """
    separate_build_folder = os.path.join(os.path.dirname(source), "build")
    package = finder.get_nearest_rez_package(source)

    if os.path.isdir(separate_build_folder) and _get_name(
        separate_build_folder
    ) == preference.get_documentation_root_name(package=package):
        # Most :ref:`rez_sphinx` configurations will use this path
        return separate_build_folder  # {rez_root}/documentation/build

    if not package:
        raise RuntimeError(
            'Directory "{source}" isn\'t in a Rez package. '
            "This is likely a rez_sphinx bug.".format(
                source=source,
            )
        )

    root = finder.get_package_root(package)
    build_directory = os.path.join(  # Usually {rez_root}/build
        root,
        config.build_directory,  # pylint: disable=no-member
    )

    return os.path.join(  # {rez_root}/build/documentation
        build_directory, preference.get_documentation_root_name(package=package)
    )


def get_documentation_source(directory):
    """Find the directory which contains `Sphinx conf.py`_ or fail trying.

    Args:
        root (str):
            A directory on-disk to search within for the `Sphinx conf.py`_.

    Raises:
        NoDocumentationFound:
            If ``root`` needs to initialize some documentation.

    Returns:
        tuple[rez.packages.Package, str]:
            Rez package + The parent directory of `Sphinx conf.py`_.

    """
    package = finder.get_nearest_rez_package(directory)

    if not package:
        raise exception.NoPackageFound(
            'Directory "{directory}" is not in a Rez source package.'.format(
                directory=directory
            )
        )

    try:
        return package, doc_finder.get_source_from_package(package)
    except RuntimeError:
        raise exception.NoDocumentationFound(
            'Directory "{root}" has no documentation. '
            "Run `rez_sphinx init` to fix this.".format(
                root=finder.get_package_root(package),
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
        SphinxExecutionError:
            If `sphinx-build`_ failed midway before it could be completed.

    Returns:
        str: The directory on-disk where the built documentation now lives.

    """
    package, source_directory = get_documentation_source(directory)

    if preference.check_default_files(package=package):
        _validate_non_default_files(source_directory)

    api_options = preference.get_api_options(options=api_options, package=package)
    build_directory = get_documentation_build(source_directory)

    if os.path.isdir(build_directory):
        _clear_directory(build_directory)

    parts = [
        "-b",
        "html",  # Always assume .html output
        source_directory,
        build_directory,
    ]

    if not os.path.isdir(build_directory):
        os.makedirs(build_directory)

    api_mode = api_builder.get_from_label(api_mode)
    package = finder.get_nearest_rez_package(directory)

    if (
        not no_api_doc
        and preference.is_api_enabled(package=package)
        and api_mode.execute
    ):
        api_mode.execute(source_directory, options=api_options)

    try:
        sphinx_build.main(parts)
    except SystemExit:
        raise exception.SphinxExecutionError(
            "sphinx-build failed. See the help, below:\n\n{help_}".format(
                help_=sphinx_build.get_parser().format_help(),
            )
        )

    return build_directory
