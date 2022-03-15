"""A collection of functions for modifying in-memory Rez packages."""

import logging
import os

from python_compatibility import wrapping
from rez_bump import rez_bump_api
from rez_industry import api
from rez_utilities import finder

from ..preferences import preference

_CURRENT_DIRECTORY = os.path.dirname(os.path.realpath(__file__))
_LOGGER = logging.getLogger(__name__)


def _add_rez_tests(package):
    """Add `rez tests attribute`_ values to make :ref:`rez_sphinx` auto-run.

    Args:
        package (:class:`rez.developer_package.DeveloperPackage`):
            The package to directly modify.

    """

    def _get_package_text(package):
        with open(package.filepath, "r") as handler:
            return handler.read()

    def _replace_package(package, text):
        path = package.filepath

        _LOGGER.info('Package "%s" will be modified.', path)

        with open(path, "w") as handler:
            handler.write(text)

    tests = package.tests or dict()
    build_key = preference.get_build_documentation_key()

    rez_sphinx_package = finder.get_nearest_rez_package(_CURRENT_DIRECTORY)
    major = int(str(rez_sphinx_package.version.major))
    minor = int(str(rez_sphinx_package.version.minor))
    next_ = major + 1

    tests[build_key] = {
        "command": "rez_sphinx build",
        "requires": [
            "rez_sphinx-{major}.{minor}+<{next_}".format(
                major=major,
                minor=minor,
                next_=next_,
            ),
        ],
    }

    original = _get_package_text(package)

    with wrapping.silence_printing():
        results = api.add_to_attribute("tests", tests, original, serialize=True)

    _replace_package(package, results)


def _bump_minor_version(package):
    """Increment the minor version of ``package``.

    E.g. version before / after

    1.2.3 -> 1.3.0
    4.5.6-beta.1 -> 4.6.0

    Note:
        If ``package`` has no valid version, this function does not nothing.

    Args:
        package (:class:`rez.developer_package.DeveloperPackage`):
            The package to directly modify.

    """
    if not package.version:
        # TODO : Add a test case for this
        _LOGGER.warning(
            'Package "%s" version will not be bumped because it has no version.',
            package,
        )

        return

    rez_bump_api.bump(package, minor=1, absolute=False, normalize=True)


def _re_acquire_package(package):
    """Re-initialize ``package``.

    Since the functions in this module directly modify ``package``, it's a good
    idea to just re-get the package from scratch so its values may be re-cached.

    Args:
        package (:class:`rez.developer_package.DeveloperPackage`):
            The out-of-date package which needs to be "refreshed".

    Returns:
        :class:`rez.developer_package.DeveloperPackage`: The refreshed package.

    """
    directory = finder.get_package_root(package)

    return finder.get_nearest_rez_package(directory)


def initialize_rez_package(package):
    """Update ``package`` to make it "work" with :ref:`rez_sphinx`.

    Args:
        package (:class:`rez.developer_package.DeveloperPackage`):
            The package to directly modify.

    """
    _bump_minor_version(package)
    _add_rez_tests(package)

    # TODO : Hopefully we won't actually need to do this
    # _add_help_attribute(package)

    return _re_acquire_package(package)
