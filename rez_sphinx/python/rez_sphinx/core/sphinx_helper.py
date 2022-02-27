import os

_SPHINX_NAME = "conf.py"


def _scan_for_configuration_path(directory):
    for root, _, files in os.walk(directory):
        for name in files:
            if name == _SPHINX_NAME:
                return os.path.join(root, name)

    raise RuntimeError(
        'Directory "{directory}" has no inner conf.py file.'.format(directory=directory)
    )


def find_configuration_path(root):
    for path in (
        os.path.join(root, "source", _SPHINX_NAME),  # rez-sphinx's default location
        os.path.join(root, _SPHINX_NAME),  # Another common, non-default spot
    ):
        if os.path.isfile(path):
            return path

    return _scan_for_configuration_path(root)
