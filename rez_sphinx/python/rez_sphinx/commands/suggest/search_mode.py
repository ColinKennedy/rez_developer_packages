def _flat():
    raise ValueError()


def _recursive():
    raise ValueError()


DEFAULT = "flat"

CHOICES = {
    DEFAULT: _flat,
    "recursive": _recursive,
}
