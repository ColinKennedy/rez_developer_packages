# TODO : Consider moving these functions to rez_utilities

import itertools

from rez.config import config
from rez import serialise


def get_valid_package_names():
    """set[str]: Find every Rez package name. e.g. ``{"package.py", "package.yaml"}``."""
    # TODO : Consider modifying finder.get_nearest_rez_package with this
    package_file_names = config.plugins.package_repository.filesystem.package_filenames
    extensions = {
        extension
        for extensions_ in serialise.FileFormat.__members__.values() for extension in extensions_.value
    }

    output = set()

    for name, extension in itertools.product(package_file_names, extensions):
        output.add("{name}.{extension}".format(name=name, extension=extension))

    return output
