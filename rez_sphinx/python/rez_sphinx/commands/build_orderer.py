"""A set of functions for implementing :ref:`rez_sphinx suggest build-order`."""

import collections
import logging
import os

import six
from rez_utilities import finder

from ..core import constant, exception, sphinx_helper
from ..preferences import preference

_LOGGER = logging.getLogger(__name__)


def _in_help(label, help_):
    """Check if ``label`` is in ``help_``.

    Args:
        label (str):
            A phrase to search with ``help_`` for. e.g. ``"Foo"``.
        help_ (list[list[str, str]] or str or None):
            The defined `help`_, if any. e.g. ``[["Foo", "README.md"]]``

    Returns:
        bool: If ``label`` is in ``help_``, return True.

    """
    if not help_:
        return False

    if isinstance(help_, six.string_types):
        return False

    return any(entry_label == label for entry_label, _ in help_)


def collect_packages(directories, searcher):
    """Check ``directories`` for Rez packages.

    Args:
        directories (iter[str]):
            The absolute path to folders on-disk to look within. It's not
            required for Rez packages to be located directly under each folder.
            And often, they are not.
        searcher (callable[str] -> list[rez.packages.Package]):
            A function which searches within ``directories`` for Rez packages
            and returns those results. These Rez packages could be source
            packages **or** installed packages.

    Raises:
        PackageConflict:
            If any Rez package was found in more than one of the listed
            directories.

    Returns:
        list[rez.packages.Package]: The found packages.

    """
    packages = []
    found_names = collections.defaultdict(set)
    found_uuids = dict()
    invalids = collections.defaultdict(set)

    for directory in directories:
        for package in searcher(directory):
            if package.uuid:
                if package.uuid in found_uuids:
                    invalids[package.name].add(directory)

                    continue

                found_uuids[package.uuid] = package.name

            if package.name in found_names:
                invalids[package.name].add(directory)

                continue

            found_names[package.name].add(directory)
            packages.append(package)

    if not invalids:
        return packages

    blob = "Multiple packages found when we expected one:\n"

    for package_name, directories_ in invalids.items():
        directories_.update(found_names[package_name])

        blob += "\n{package_name}: {directories_}".format(
            package_name=package_name,
            directories_=", ".join(sorted(directories_)),
        )

    raise exception.PackageConflict(blob)


def filter_existing_documentation(packages):
    """Remove any Rez package from ``packages`` which already has documentation.

    This function uses a variety of checks including searching "known"
    documentation locations. As well as guessing where it could be.

    This function searches specifically for `Sphinx`_ documentation only.

    Args:
        packages (list[rez.packages.Package]):
            The source / installed Rez packages to filter. Usually,
            these are source Rez packages.

    Returns:
        list[rez.packages.Package]:
            Every package from ``packages`` which doesn't have documentation.

    """
    output = []

    for package in packages:
        # Check if ``package`` is an installed, auto-generated package
        if _in_help(constant.REZ_SPHINX_OBJECTS_INV, package.help):
            _LOGGER.debug(
                'Package "%s" will be skipped. It already has an objects.inv.',
                package.name,
            )

            continue

        package_root = finder.get_package_root(package)

        # Check if ``package`` is a source package
        documentation_top = os.path.join(
            package_root,
            preference.get_documentation_root_name(),
        )

        if os.path.isdir(documentation_top):
            _LOGGER.debug(
                'Package "%s" will be skipped. It has a documentation folder.',
                package.name,
            )

            continue

        try:
            configuration = sphinx_helper.find_configuration_path(package_root)
        except RuntimeError:
            pass
        else:
            _LOGGER.debug(
                'Package "%s" will be skipped. It has a conf.py "%s" file.',
                package.name,
                configuration,
            )

            continue

        output.append(package)

    return output
