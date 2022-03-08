import operator
import os

import six

from ..preferences import preference, preference_init
from . import configuration, sphinx_helper


_DEFAULT_LABEL = "Home Page"
_REZ_HELP_KEY = "help"
_SEEN = set()


def _already_processed(path):
    if path in _SEEN:
        return True

    _SEEN.add(path)

    return False


def _expand_help(help_):
    if not help_:
        return []

    if not isinstance(help_, six.string_types):
        return help_

    return [[_DEFAULT_LABEL, help_]]


def _find_help_labels(root):
    tags = set()

    for path in _iter_sphinx_source_files(root):
        fallback_name = os.path.splitext(os.path.relpath(path, root))[0]
        # TODO : Consider making this a non-hard-coded value
        fallback_destination = fallback_name + ".html"

        for label, destination in _get_rez_sphinx_tags(path):
            if not destination:
                destination = fallback_destination

            tags.add((label, destination))

    return tags


def _get_rez_sphinx_tags(path):
    with open(path, "r") as handler:
        data = handler.read()

    return preference_init.find_tags(data.split("\n"))


def _iter_sphinx_source_files(root):
    sphinx = configuration.ConfPy.from_directory(root)
    extension = sphinx.get_source_extension()

    for current_root, _, files in os.walk(root):
        for name in files:
            if name.endswith(extension):
                yield os.path.join(current_root, name)


def package_preprocess_function(this, data):
    package_source_root = os.getcwd()

    if _already_processed(package_source_root):
        return

    help_ = _expand_help(data.get(_REZ_HELP_KEY))
    documentation_root = os.path.join(package_source_root, preference.get_documentation_root_name())

    if not os.path.isdir(documentation_root):
        return

    source_path = sphinx_helper.find_configuration_path(documentation_root)
    source_root = os.path.dirname(source_path)

    help_.extend(_find_help_labels(source_root))
    help_ = sorted(help_, key=operator.itemgetter(0))

    data[_REZ_HELP_KEY] = help_
