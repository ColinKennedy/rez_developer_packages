import glob
import os

from rez import developer_package


def _get_packages(directories):
    return [developer_package.DeveloperPackage.from_path(directory) for directory in directories]


def _installed(root):
    paths = glob.glob(os.path.join(root, "*", "*"))

    return _get_packages(paths)


def _source(root):
    paths = glob.glob(os.path.join(root, "*"))

    return _get_packages(paths)


def _recursive():
    raise ValueError()


def get_mode_by_name(name):
    try:
        return CHOICES[name]
    except KeyError:
        raise ValueError(
            'Name "{name}" is invalid. The options were, "{options}".'.format(
                name=name, options=sorted(CHOICES.keys()))
        )


DEFAULT = "source"

CHOICES = {
    DEFAULT: _source,
    "installed": _installed,
    "recursive": _recursive,
}
