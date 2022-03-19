import glob
import os

from rez import developer_package


def _is_valid_rez_package(text):
    # TODO : Replace with something more dynamic, here
    return text in {"package.py", "package.yaml", "package.yml", "package.txt"}


def _get_packages(directories):
    return [developer_package.DeveloperPackage.from_path(directory) for directory in directories]


def _installed(root):
    paths = glob.glob(os.path.join(root, "*", "*"))

    return _get_packages(paths)


def _source(root):
    paths = glob.glob(os.path.join(root, "*"))

    return _get_packages(paths)


def _recursive(top):
    output = []

    for root, _, files in os.walk(top):
        for name in files:
            if not _is_valid_rez_package(name):
                continue

            # TODO : Add invalid checking here
            output.append(developer_package.DeveloperPackage.from_path(root))

    return output


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
