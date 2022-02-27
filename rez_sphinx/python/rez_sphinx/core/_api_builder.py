"""A companion module to :mod:`api_builder` which builds the API .rst files."""

import os

from . import path_control


def generate_api_files(directory):
    api_directory = os.path.join(directory, "api")

    if not os.path.isdir(api_directory):
        os.makedirs(api_directory)

    path_control.clear_directory(api_directory)
    path_control.add_gitignore(api_directory)
