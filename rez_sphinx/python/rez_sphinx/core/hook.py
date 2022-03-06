import operator
import os

from rez_utilities import finder
import six

from ..preferences import preference, preference_init
from . import configuration, sphinx_helper


_DEFAULT_LABEL = "Home Page"
_REZ_HELP_KEY = "help"


def _expand_help(help_):
    if not help_:
        return []

    if not isinstance(help_, six.string_types):
        return help_

    return [[_DEFAULT_LABEL, help_]]


def _find_help_labels(root):
    tags = set()

    for path in _iter_sphinx_source_files(root):
        tags.update(_get_rez_sphinx_tags(path))

    return tags


def _get_rez_sphinx_tags(path):
    with open(path, "r") as handler:
        data = handler.read()

    raise NotImplementedError("Need to write this")

    for label, destination in preference_init.find_tags(data.split("\n")):
        raise NotImplementedError(label, destination)


def _iter_sphinx_source_files(root):
    path = sphinx_helper.find_configuration_path(
        os.path.join(root, preference.get_documentation_root_name())
    )
    sphinx = configuration.ConfPy.from_path(path)
    extension = sphinx.get_source_extension()

    for current_root, _, files in os.walk(root):
        for name in files:
            if name.endswith(extension):
                yield os.path.join(current_root, name)


def package_preprocess_function(this, data):
    help_ = _expand_help(data.get(_REZ_HELP_KEY))
    root = finder.get_package_root(this)
    help_.extend(_find_help_labels(root))
    help_ = sorted(help_, key=operator.itemgetter(0))

    data[_REZ_HELP_KEY] = help_
