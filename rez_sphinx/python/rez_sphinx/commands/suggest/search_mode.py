"""Implement all code for :ref:`build-order --search-mode`."""

import glob
import os

from rez import developer_package


def _is_valid_rez_package(text):
    """bool: Check if ``text`` is a valid Rez package name."""
    # TODO : Replace with something more dynamic, here
    return text in {"package.py", "package.yaml", "package.yml", "package.txt"}


def _get_packages(directories):
    """list[:class:`rez.developer_package.DeveloperPackage`]: Every found package."""
    return [developer_package.DeveloperPackage.from_path(directory) for directory in directories]


def _installed(root):
    """Find all installed Rez packages, starting from ``root``.

    Args:
        root (str):
            The absolute directory to an installed Rez package location. Common
            examples include ``"~/packages"``, ``"~/.rez/packages/int"``, etc.

    Returns:
        list[:class:`rez.developer_package.DeveloperPackage`]: Every found package.

    """
    paths = glob.glob(os.path.join(root, "*", "*"))

    return _get_packages(paths)


def _source(root):
    """Find all installed Rez packages, starting from ``root``.

    Important:
        This function **assumes** that your Rez packages are laid out in a flat,
        simple style which is most common for source Rez packages.

        This function is **not** for installed Rez packages. See
        :func:`_installed` instead.

    Args:
        root (str):
            The absolute directory to a top-level directory containing folders
            of source Rez packages. This directory is typically in a git
            repository, **not** ``"~/packages"``, ``"~/.rez/packages/int"``, etc.

    Returns:
        list[:class:`rez.developer_package.DeveloperPackage`]: Every found package.

    """
    paths = glob.glob(os.path.join(root, "*"))

    return _get_packages(paths)


def _recursive(top):
    """Search blindly for Rez packages, starting from ``root``.

    Args:
        top (str): The absolute directory where Rez packages may live underneath.

    Returns:
        list[:class:`rez.developer_package.DeveloperPackage`]: Every found package.

    """
    output = []

    for root, _, files in os.walk(top):
        for name in files:
            if not _is_valid_rez_package(name):
                continue

            # TODO : Add invalid checking here
            output.append(developer_package.DeveloperPackage.from_path(root))

    return output


def get_mode_by_name(name):
    """Find a callable function matching ``name``.

    Args:
        name (str):
            A registered possibility, e.g. ``"source"``, ``"installed"``, or
            ``"guess"``.

    Raises:
        ValueError: If ``name`` is not a registered command.

    Returns:
        callable[str] -> list[:class:`rez.developer_package.DeveloperPackage`]:
            A function that takes an absolute directory path and then finds all
            Rez packages that it can, underneath the directory.

    """
    try:
        return CHOICES[name]
    except KeyError:
        raise ValueError(
            'Name "{name}" is invalid. The options were, "{options}".'.format(
                name=name, options=sorted(CHOICES.keys()))
        )


DEFAULT = "source"

CHOICES = {
    DEFAULT: _source,
    "installed": _installed,
    "recursive": _recursive,
}
