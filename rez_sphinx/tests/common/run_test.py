"""Make running :ref:`rez_sphinx` in unittests easier."""

import contextlib
import copy
import os
import shlex
import sys

import six
from rez.config import config as config_
from rez_utilities import finder

from rez_sphinx import cli
from rez_sphinx.core import path_control
from rez_sphinx.preferences import preference


@contextlib.contextmanager
def allow_defaults():
    """Allow users to run :ref:`rez_sphinx build run` even with default files."""
    with keep_config() as config:
        config.optionvars.setdefault("rez_sphinx", {})
        config.optionvars["rez_sphinx"].setdefault("init_options", {})
        config.optionvars["rez_sphinx"]["init_options"]["check_default_files"] = False

        yield


def clear_caches():
    """Delete all caches which might otherwise affect unittest logic."""
    preference.get_base_settings.cache_clear()


@contextlib.contextmanager
def keep_config():
    """Temporarily allow edits to `rez-config`_ for the scope of this function.

    Yields:
        module: The Rez temporary config object to modify.

    """
    # TODO : Figure out a more reliable way to clear the cached config, if any
    # Remove any caching so it can be evaluated again
    preference.get_base_settings.cache_clear()

    package_definition_build_python_paths = copy.deepcopy(
        config_.package_definition_build_python_paths
    )
    optionvars = copy.deepcopy(config_.optionvars)
    package_preprocess_function = config_.package_preprocess_function
    plugin_path = copy.deepcopy(config_.plugin_path)
    release_hooks = copy.deepcopy(config_.release_hooks)

    try:
        yield config_
    finally:
        config_.optionvars = optionvars
        config_.package_definition_build_python_paths = (
            package_definition_build_python_paths
        )
        config_.package_preprocess_function = package_preprocess_function
        config_.plugin_path = plugin_path
        config_.release_hooks = release_hooks


@contextlib.contextmanager
def simulate_resolve(installed_packages):
    """Make a resolve with ``installed_packages`` and :ref:`rez_sphinx`."""
    original_environment = os.environ.copy()
    original_path = sys.path[:]

    for installed_package in installed_packages:
        root = finder.get_package_root(installed_package)

        upper = path_control.to_environment_name(installed_package.name)
        os.environ["REZ_{upper}_ROOT".format(upper=upper)] = root

        directory = os.path.join(root, "python")

        if os.path.isdir(directory):
            sys.path.append(directory)

    try:
        yield
    finally:
        sys.path = original_path
        os.environ.clear()
        os.environ.update(original_environment)


def test(text):
    """Run ``text`` as if it were run from the terminal.

    Args:
        text (list[str] or str):
            The raw arguments to pass to the "terminal".
            e.g. "build /path/to/directory" or "init".

    """
    parts = text

    if isinstance(parts, six.string_types):
        parts = shlex.split(parts)

    cli.main(parts)
