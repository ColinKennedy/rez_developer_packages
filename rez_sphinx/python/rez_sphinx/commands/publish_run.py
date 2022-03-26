import logging
import os

from rez_utilities import finder
from rez import package_test
import six

try:
    from functools import lru_cache  # Python 3.2+
except ImportError:
    from backports.functools_lru_cache import lru_cache

from ..core import exception
from ..preferences import preference


_LOGGER = logging.getLogger(__name__)


def _get_documentation_destination(name, package):
    def _parse_destination(text):
        raise ValueError(text)

    test = package.tests[name]

    if isinstance(test, six.string_types):
        return _parse_destination(test)

    # TODO : Consider replacing with a global variable?
    return _parse_destination(test["command"])


@lru_cache()
def _get_fallback_destination():
    raise NotImplementedError("Need to write this")


def _validated_test_keys(runner):
    tests = runner.get_test_names()

    if not tests:
        raise exception.BadPackage(
            'Package "{package}" has no ``tests`` attribute.'.format(
                package=runner.get_package(),
            )
        )

    # TODO : It may make more sense to add a
    # `preference.get_publish_documentation_keys` and have that list default to
    # `preference.get_build_documentation_keys` if it is not defined. That way
    # users can specify publish keys differently than build ones.
    #
    build_tests = preference.get_build_documentation_keys()
    names = [name for name in build_tests if name in tests]

    if names:
        return names

    name = runner.get_package().name

    raise exception.BadPackage(
        'Package "{name}" has no rez_sphinx key for building documentation. '
        "Run ``rez_sphinx init`` to fix this.".format(name=name)
    )


def is_publishing_enabled():
    """bool: Check if the user's current environment is capable of publishing."""
    return os.getenv("REZ_EPH_REZ_SPHINX_FEATURE_DOCBOT_PLUGIN_REQUEST", "0").endswith(
        "1"
    )


def build_documentation(directory):
    def _to_exact_request(package):
        # TODO : Check if Rez has a function for this
        if not package.version:
            return package.name

        return "{package.name}=={package.version}".format(package=package)

    package = finder.get_nearest_rez_package(directory)
    runner = package_test.PackageTestRunner(package_request=_to_exact_request(package))
    tests = _validated_test_keys(runner)

    _LOGGER.info('Found "%s" documentation tests.', tests)

    output = []

    for name in tests:
        _LOGGER.info('Now building documentation with "%s".', name)

        runner.run_test(name)
        output.append(
            _get_documentation_destination(name, package) or _get_fallback_destination()
        )

    return output


def publish(root):
    raise ValueError(root)
