import collections
import operator

from ...core import package_query


def _compute_package_depth(package, all_family_names):
    def _compute(package, seen, computed_depths):
        dependencies = package_query.get_dependencies(package)
        depths = set()

        for request in dependencies:
            name = request.name

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
    for package in packages:
        path = package.filepath

        with open(path, "r") as handler:
            raise NotImplementedError(handler.read())

    raise NotImplementedError('stop')


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
