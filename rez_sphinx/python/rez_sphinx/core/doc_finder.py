import os

from rez_utilities import finder


def get_source_from_directory(directory):
    # TODO : Don't hard-code "documentation" here
    documentation_name = "documentation"

    # TODO : Don't hard-code sorce
    possible_directory = os.path.join(directory, documentation_name, "source")

    if os.path.isdir(possible_directory):
        return possible_directory

    possible_directory = os.path.join(directory, documentation_name)

    if os.path.isdir(possible_directory):
        return possible_directory

    raise ValueError(
        'Directory "{directory}" has no documentation.'.format(directory=directory)
    )


def get_source_from_package(package):
    root = finder.get_package_root(package)

    return get_source_from_directory(root)
