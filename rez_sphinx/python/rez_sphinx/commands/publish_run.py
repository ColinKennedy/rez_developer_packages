import logging
import os

import six
from rez import package_test
from rez_utilities import finder

try:
    from functools import lru_cache  # Python 3.2+
except ImportError:
    from backports.functools_lru_cache import lru_cache

from ..core import exception
from ..preferences import preference

_LOGGER = logging.getLogger(__name__)


def _get_documentation_destination(name, package):
    """Find the directory where built documentation now lives.

    This function assumes that ``name`` has already been run at least once.

    Args:
        name (str):
            The name of the Rez `tests`_ key that ran.
        package (rez.packages.Package):
            The package which defines `name`_ and was ran from.

    Returns:
        str: The found documentation directory.

    """

    def _parse_destination(text):
        raise ValueError(text)

    test = package.tests[name]

    if isinstance(test, six.string_types):
        return _parse_destination(test)

    # TODO : Consider replacing with a global variable?
    return _parse_destination(test["command"])


@lru_cache()
def _get_fallback_destination():
    # TODO : Add docstring here once it's implemented
    raise NotImplementedError("Need to write this")


def _validated_test_keys(runner):
    """Get every :ref:`rez_sphinx`-registered `tests`_ key in ``runner``.

    Since :ref:`rez_sphinx.build_documentation_key` may be multiple values, we
    must check and return every matching key in ``runner``.

    Args:
        runner (rez.package_test.PackageTestRunner): The Rez package to query from.

    Raises:
        BadPackage:
            If ``runner`` has no tests or the defined tests have nothing in
            common with :ref:`rez_sphinx.build_documentation_key`.

    Returns:
        list[str]:
            Every found, matching key. In most cases, this will return either
            ``["build_documentation"]``, which is the default
            :ref:`rez_sphinx.build_documentation_key`, or nothing.

    """
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
    """Build all :ref:`rez_sphinx` registered documentation at ``directory``.

    Args:
        directory (str):
            The absolute path to a folder on disk. This folder should be
            a sub-folder inside of a Rez package to the root of the Rez package.

    Raises:
        NoDocumentationFound:
            If any found `tests`_ attributes ran, succeeded to run, but no
            destination documentation could be found.

    Returns:
        list[str]:
            The root directories on-disk where all documentation was generated
            into. For typical users, this list contains only one value.

    """

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
    invalids = set()

    for name in tests:
        _LOGGER.info('Now building documentation with "%s".', name)

        runner.run_test(name)
        destination = (
            _get_documentation_destination(name, package) or _get_fallback_destination()
        )

        if not destination:
            invalids.add(name)

        output.append(destination)

    if invalids:
        raise exception.NoDocumentationFound(
            "No documentation could be found after "
            '"{invalids}" commands were ran.'.format(invalids=", ".sorted(invalids))
        )

    return output


def publish(root):
    raise ValueError(root)
