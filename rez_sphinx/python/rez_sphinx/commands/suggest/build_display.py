"""Implement all code for :ref:`build-order --display-as`."""

from __future__ import print_function

import operator

from rez_utilities import finder


def _directories(all_packages):
    for package in (
        package
        for packages in all_packages
        for package in sorted(packages, key=operator.attrgetter("name"))
    ):
        print(finder.get_package_root(package))


def _names(all_packages):
    depth = 0

    for packages in all_packages:
        print("#{depth}: {names}".format(depth=depth, names=" ".join(sorted({package.name for package in packages}))))
        depth += 1


def get_mode_by_name(name):
    try:
        return CHOICES[name]
    except KeyError:
        raise ValueError(
            'Name "{name}" is invalid. The options were, "{options}".'.format(
                name=name, options=sorted(CHOICES.keys()))
        )


DEFAULT = "directories"
CHOICES = {
    DEFAULT: _directories,
    "names": _names,
}
