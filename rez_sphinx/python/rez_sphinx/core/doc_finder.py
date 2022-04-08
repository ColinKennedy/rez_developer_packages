"""Help finding documentation-related files on-disk."""

import os

from rez_utilities import finder

from ..preferences import preference


def get_source_from_directory(directory):
    """Find the top-level documentation source root, from ``directory``.

    Args:
        directory (str): The root of a Rez package.

    Raises:
        RuntimeError: If no root could be found.

    Returns:
        str: The found documentation source root.

    """
    documentation_name = preference.get_documentation_root_name(package=package)

    # TODO : Don't hard-code source
    possible_directory = os.path.join(directory, documentation_name, "source")

    if os.path.isdir(possible_directory):
        return possible_directory

    possible_directory = os.path.join(directory, documentation_name)

    if os.path.isdir(possible_directory):
        return possible_directory

    raise RuntimeError(
        'Directory "{directory}" has no documentation.'.format(directory=directory)
    )


def get_source_from_package(package):
    """Find the top-level documentation source root, from ``package``.

    Args:
        package (rez.packages.Package): The root of a Rez package.

    Returns:
        str: The found documentation source root.

    """
    root = finder.get_package_root(package)

    return get_source_from_directory(root)
