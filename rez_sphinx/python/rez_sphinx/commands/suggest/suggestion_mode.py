"""Implement all code for :ref:`build-order --search-mode`."""

import collections
import operator

from ...core import package_query


def _get_regular_dependencies(package):
    """Grab all known / obvious dependencies from ``package``.

    Args:
        package (:class:`rez.developer_package.DeveloperPackage`):
            The source / installed Rez package to query from.

    Returns:
        set[str]:
            Each found Rez package family name which ``package`` depends on.
            This list of dependencies is "only the dependencies which
            :ref:`rez_sphinx` needs", not a full list of dependencies.

    """
    return {request.name for request in package_query.get_dependencies(package)}


def _compute_package_depth(package, all_family_names, getter=_get_regular_dependencies):
    """Determine how "deep" the dependencies ``package`` is.

    Imagine 2 packages. "no_listed_requires" and "has_a_requirement".
    "has_a_requirement" includes "no_listed_requires". This function would
    return `0` for "no_listed_requires" and `1` for "has_a_requirement".

    Args:
        package (:class:`rez.developer_package.DeveloperPackage`):
            The source / installed Rez package to query from.
        all_family_names (dict[str, :class:`rez.developer_package.DeveloperPackage`]):
            A store of possible Rez packages to consider while iterating over
            ``package``'s dependencies. Each key is a Rez package family name,
            each value is the in-memory Rez package which the family refers to.
        getter (callable[:class:`rez.developer_package.DeveloperPackage`] -> set[str]):
            The function which takes ``package`` as input and returns its
            dependencies (e.g. its `requires`_).

    Returns:
        int:
            A 0-or-more value indicating ``package``'s depth. 0 being "shallow"
            and 1+ meaning "has at least a dependency within
            ``all_family_names``". Higher values means higher dependency
            nesting.

    """

    def _compute(package, seen, computed_depths):
        depths = set()

        for name in getter(package):
            if name in computed_depths:
                depths.add(computed_depths[name])

                continue

            if name in seen:
                continue

            seen.add(name)

            if name not in all_family_names:
                continue

            if name not in computed_depths:
                computed_depths[name] = _compute(
                    all_family_names[name],
                    seen,
                    computed_depths,
                )

            depths.add(computed_depths[name])

        seen.add(package.name)

        if not depths:
            return 0

        return max(depths) + 1

    computed_depths = dict()
    seen = set()

    return _compute(package, seen, computed_depths)


def _config(packages):
    """Re-order ``packages`` based on their dependencies.

    Args:
        packages (container[:class:`rez.developer_package.DeveloperPackage`]):
            The source / installed Rez packages to re-order.

    Returns:
        list[list[:class:`rez.developer_package.DeveloperPackage`]]:
            A list with each depth's packages, starting from depth=0 and
            ascending order.

    """
    all_family_names = {package.name: package for package in packages}
    depths = collections.defaultdict(set)

    for package in packages:
        depth = _compute_package_depth(package, all_family_names)
        depths[depth].add(package)

    return [
        packages
        for _, packages in sorted(depths.items(), key=operator.itemgetter(0))
    ]


def _guess(packages):
    """Re-order ``packages`` based on their dependencies.

    Unlike :func:`_config`, this function is intentionally hacky and just looks
    for any reference to any dependency within packages. It has the potential
    to get more dependencies than :func:`_config` could, at the cost of
    possibly computing more dependencies than needed.

    Args:
        packages (container[:class:`rez.developer_package.DeveloperPackage`]):
            The source / installed Rez packages to re-order.

    Returns:
        list[list[:class:`rez.developer_package.DeveloperPackage`]]:
            A list with each depth's packages, starting from depth=0 and
            ascending order.

    """

    def _guess_dependencies(data, all_family_names):

        def wrapper(package):
            result = _get_regular_dependencies(package)
            result.update(
                {
                    name
                    for name in all_family_names
                    if name != package.name  # Prevent infinite RecursionError
                    and name in data
                }
            )

            return result

        return wrapper

    all_family_names = {package.name: package for package in packages}
    depths = collections.defaultdict(set)

    for package in packages:
        with open(package.filepath, "r") as handler:
            data = handler.read()

        _guesser = _guess_dependencies(data, set(all_family_names.keys()))

        depth = _compute_package_depth(package, all_family_names, getter=_guesser)
        depths[depth].add(package)

    return [
        packages
        for _, packages in sorted(depths.items(), key=operator.itemgetter(0))
    ]


def get_mode_by_name(name):
    """Find a callable function matching ``name``.

    Args:
        name (str): A registered possibility, e.g. ``"config"`` or ``"guess"``.

    Raises:
        ValueError: If ``name`` is not a registered command.

    Returns:
        callable[
            container[:class:`rez.developer_package.DeveloperPackage`] -> list[
                list[:class:`rez.developer_package.DeveloperPackage`]
            ]
        ]:
            A function which takes a list of Rez packages, for example, and
            returns a list with each depth's packages, starting from depth=0
            and ascending order.

    """
    try:
        return CHOICES[name]
    except KeyError:
        raise ValueError(
            'Name "{name}" is invalid. The options were, "{options}".'.format(
                name=name, options=sorted(CHOICES.keys()))
        )


DEFAULT = "config"
CHOICES = {
    DEFAULT: _config,
    "guess": _guess,
}
