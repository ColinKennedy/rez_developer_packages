import collections
import re
import logging
import os

from six import moves

import rpmfile


_LOGGER = logging.getLogger(__name__)
_Details = collections.namedtuple(
    "_Details",
    ["name", "os", "requires", "version"],
)
_MODULES = re.compile(r"\([^()]*\)")


def _get_requires(names, versions):
    requires = set()

    for name, version in moves.zip(names, versions):
        if os.path.isabs(name):
            _LOGGER.debug('Skipped: "%s" requirement.', name)

            continue

        stripped = _strip_modules(name)

        if not version:
            requires.add(stripped)

            continue

        # TODO : Determine if it needs to be exact versions here. If so, make it "=="
        requires.add("{stripped}-{version}".format(stripped=stripped, version=version))

    return sorted(requires)


def _strip_modules(name):
    return _MODULES.sub("", name)


def get_details(path):
    with rpmfile.open(path) as handler:
        headers = handler.headers

        return _Details(
            name=_strip_modules(headers["name"]),
            version=headers["version"],
            os=headers["os"],
            requires=sorted(
                _get_requires(headers["requirename"], headers["requireversion"])
            ),
        )
