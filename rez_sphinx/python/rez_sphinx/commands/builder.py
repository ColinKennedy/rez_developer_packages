import os

from sphinx.cmd import build as sphinx_build
from rez.config import config
from rez_utilities import finder

from ..core import sphinx_helper


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
    build_directory = os.path.join(root, config.build_directory)  # {rez_root}/build

    return os.path.join(build_directory, "documentation")  # {rez_root}/build/documentation


def _get_documentation_source(root):
    """Find the directory which contains :ref:`Sphinx conf.py` or fail trying.

    Args:
        root (str):
            A directory on-disk to search within for the
            :ref:`Sphinx conf.py <conf.py>`.

    Returns:
        str: The parent directory of :ref:`Sphinx conf.py <conf.py>`.

    """
    configuration = sphinx_helper.find_configuration_path(root)

    return os.path.dirname(configuration)


def build(directory, api_mode=api_builder.Mode.full_auto):
    """Generate .html files from the Sphinx documentation in ``directory``.

    Args:
        directory (str):
            The absolute path to a root Rez package.
        api_mode (str):
            A description of what to do about Python API documentation.
            For example, should it be generated or not? See
            :mod:`api_builder` for details.

    """
    # TODO : Add mode support
    source_directory = _get_documentation_source(directory)
    build_directory = _get_documentation_build(source_directory)
    parts = [
        directory,
        "-b", "html",  # Always assume .html output
        source_directory,
        build_directory,
    ]

    sphinx_build.main(parts)
