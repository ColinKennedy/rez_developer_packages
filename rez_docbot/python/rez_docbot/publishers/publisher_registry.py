from ..publishers import github


_PUBLISHERS = {
    github.Github.get_name(): github.Github,
}


def get_by_name(name):
    try:
        return _PUBLISHERS[name]
    except KeyError:
        raise ValueError(
            'Name "{name}" is invalid. Options were, "{options}".'.format(
                name=name,
                options=sorted(_PUBLISHERS.keys()),
            )
        )
