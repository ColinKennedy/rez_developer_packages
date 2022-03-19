import collections
import operator

from ...core import package_query


def _get_regular_dependencies(package):
    return {request.name for request in package_query.get_dependencies(package)}


def _compute_package_depth(package, all_family_names, dependencies_getter=_get_regular_dependencies):
    def _compute(package, seen, computed_depths):
        depths = set()

        for name in dependencies_getter(package):
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

        try:
            return max(depths) + 1
        except ValueError:
            # Python errors if ``depths`` is empty
            return 0

    computed_depths = dict()
    seen = set()

    return _compute(package, seen, computed_depths)


def _config(packages):
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

    def _guess_dependencies(data, all_family_names):

        def wrapper(package):
            result = _get_regular_dependencies(package)
            # {
            #     name
            #     for name in all_family_names
            #     if name != package.name  # Prevent infinite RecursionError
            #     and name in data
            # }
            # )
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

        depth = _compute_package_depth(package, all_family_names, dependencies_getter=_guesser)
        depths[depth].add(package)

    return [
        packages
        for _, packages in sorted(depths.items(), key=operator.itemgetter(0))
    ]


def get_mode_by_name(name):
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
