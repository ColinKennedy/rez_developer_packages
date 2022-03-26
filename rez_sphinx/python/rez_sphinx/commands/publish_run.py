import logging
import os

from rez_utilities import finder

from ..core import exception
from ..preferences import preference


_LOGGER = logging.getLogger(__name__)


def _get_runner(package):
    for key in build_tests:
        if key in tests:
            raise ValueError()


def _validated_test_keys(package):
    tests = package.tests

    if not tests:
        raise exception.BadPackage(
            'Package "{package.name}" has no ``tests`` attribute.'.format(package=package),
        )

    build_tests = preference.get_build_documentation_keys()
    names = [name for name in build_tests if name in tests]

    if names:
        return names

    raise exception.BadPackage(
        'Package "{package.name}" has no rez_sphinx key for building documentation. '
        'Run ``rez_sphinx init`` to fix this.'.format(package=package)
    )


def is_publishing_enabled():
    """bool: Check if the user's current environment is capable of publishing."""
    return os.getenv("REZ_EPH_REZ_SPHINX_FEATURE_DOCBOT_PLUGIN_REQUEST", "0").endswith("1")


def build_documentation(directory):
    package = finder.get_nearest_rez_package(directory)

    tests = _validated_test_keys(package)

    _LOGGER.info('Now building documentation using "%s" tests.', tests)
    _get_runner(package, tests)
    raise ValueError(directory)
