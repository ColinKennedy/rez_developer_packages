"""Implement all code for :ref:`build-order --display-as`.

There are 2 modes supported by default:

- "directories" - Shows results as pure folder paths. Useful for scripting.
- "names" - Shows results as concise Rez package names. Useful for reading.

"""

from __future__ import print_function

import operator

from rez_utilities import finder


def _directories(all_packages):
    """Print the directories for every Rez package in ``packages``.

    Args:
        all_packages (list[list[rez.packages.Package]]):
            Each package to print, ordered by relative "dependency depth".

    """
    for package in (
        package
        for packages in all_packages
        for package in sorted(packages, key=operator.attrgetter("name"))
    ):
        print(finder.get_package_root(package))


def _names(all_packages):
    """Print every Rez package name in ``packages``.

    Args:
        all_packages (list[list[rez.packages.Package]]):
            Each package to print, ordered by relative "dependency depth".

    """
    depth = 0

    for packages in all_packages:
        print(
            "#{depth}: {names}".format(
                depth=depth,
                names=" ".join(sorted({package.name for package in packages})),
            )
        )
        depth += 1


def get_mode_by_name(name):
    """Find a callable function matching ``name``.

    Args:
        name (str):
            A registered possibility, e.g. ``"names"`` or ``"directories"``.

    Raises:
        ValueError: If ``name`` is not a registered command.

    Returns:
        callable[list[list[rez.packages.Package]]]:
            Each package to print, ordered by relative "dependency depth".

    """
    try:
        return CHOICES[name]
    except KeyError:
        raise ValueError(
            'Name "{name}" is invalid. The options were, "{options}".'.format(
                name=name, options=sorted(CHOICES.keys())
            )
        )


DEFAULT = "directories"
CHOICES = {
    DEFAULT: _directories,
    "names": _names,
}
