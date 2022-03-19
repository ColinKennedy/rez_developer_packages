def _directories():
    raise ValueError()


def _names():
    raise ValueError()


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
