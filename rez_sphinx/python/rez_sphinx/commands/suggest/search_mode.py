"""Implement all code for :ref:`build-order --search-mode`."""

import logging
import glob
import os

from rez import developer_package, exceptions as rez_exceptions

from ...core import exception


_COMMON_REZ_EXCEPTIONS = (
    rez_exceptions.PackageMetadataError,  # When package.py lacks data
    rez_exceptions.ResourceError,  # When package.py isn't parse-able
)
_LOGGER = logging.getLogger(__name__)


def _is_valid_rez_package(text):
    """bool: Check if ``text`` is a valid Rez package name."""
    # TODO : Replace with something more dynamic, here
    return text in {"package.py", "package.yaml", "package.yml", "package.txt"}


def _get_packages(directories):
    """Every found package.

    Important:
        This function assumes that every directory in ``directories``
        definitely has a valid Rez package definition. If there isn't one, this
        function fails.

    Raises:
        :class:`.BadPackage`:
            If a directory in ``directories`` has no package definition file or
            it is invalid.

    Returns:
        list[:class:`rez.developer_package.DeveloperPackage`]: The found packages.

    """
    packages = []
    invalids = set()

    for directory in directories:
        try:
            packages.append(developer_package.DeveloperPackage.from_path(directory))
        except _COMMON_REZ_EXCEPTIONS:
            invalids.add(
                'Path "{directory}" has missing / invalid schema data.'.format(
                    directory=directory,
                )
            )

    if not invalids:
        return packages

    raise exception.BadPackage(
        "Found directories with missing / invalid Rez packages:\n{blob}".format(
            blob="\n".join(sorted(invalids))
        )
    )


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
            try:
                output.append(developer_package.DeveloperPackage.from_path(root))
            except _COMMON_REZ_EXCEPTIONS:
                _LOGGER.debug('Skipped "%s". Its package is invalid.', root)

                continue

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
                name=name, options=sorted(CHOICES.keys())
            )
        )


DEFAULT = "source"

CHOICES = {
    DEFAULT: _source,
    "installed": _installed,
    "recursive": _recursive,
}
