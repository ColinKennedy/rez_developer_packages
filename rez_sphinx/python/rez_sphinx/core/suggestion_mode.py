def _config():
    raise ValueError()


def _guess():
    raise ValueError()


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
