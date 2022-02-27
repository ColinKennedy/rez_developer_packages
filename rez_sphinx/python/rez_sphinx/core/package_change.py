import logging
import os

from rez_bump import rez_bump_api
from rez_utilities import finder

from . import preference

_CURRENT_DIRECTORY = os.path.dirname(os.path.realpath(__file__))
_LOGGER = logging.getLogger(__name__)


def _add_rez_tests(package):
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
        ]
    }

    raise ValueError('Apply to the package here')


def _bump_minor_version(package):
    if not package.version:
        _LOGGER.warning(
            'Package "%s" version will not be bumped because it has no version.',
            package,
        )

        return

    rez_bump_api.bump(package, minor=1, absolute=False, normalize=True)


def _re_acquire_package(package):
    directory = finder.get_package_root(package)

    return finder.get_nearest_rez_package(directory)


def initialize_rez_package(package):
    _bump_minor_version(package)
    _add_rez_tests(package)

    # TODO : Hopefully we won't actually need to do this
    # _add_help_attribute(package)

    return _re_acquire_package(package)
