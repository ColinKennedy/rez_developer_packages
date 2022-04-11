"""A set of functions for implementing :ref:`rez_sphinx suggest build-order`."""

import collections
import logging

from ..core import exception

_LOGGER = logging.getLogger(__name__)


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
    found_uuids = {}
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
