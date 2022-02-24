import collections
import re
import logging
import os

from six import moves

import rpmfile


_LOGGER = logging.getLogger(__name__)
_RpmDetails = collections.namedtuple(
    "_RpmDetails",
    ["name", "os", "path", "requires", "version"],
)
_MODULES = re.compile(r"\([^()]*\)")


def _get_requires(names, versions):
    requires = set()

    for name, version in moves.zip(names, versions):
        if os.path.isabs(name):
            _LOGGER.debug('Skipped: "%s" requirement.', name)

            continue

        stripped = _strip_modules(name)
        rezified = _rezify_name(stripped)

        if not version:
            requires.add(rezified)

            continue

        # TODO : Determine if it needs to be exact versions here. If so, make it "=="
        requires.add("{rezified}-{version}".format(rezified=rezified, version=version))

    return sorted(requires)


def _rezify_name(name):
    # TODO : Replace this with rez-pip's function. Need to find it first though
    return name.replace("-", "_")


def _strip_modules(name):
    return _MODULES.sub("", name)


def get_details(path):
    with rpmfile.open(path) as handler:
        headers = handler.headers
        name = _strip_modules(headers["name"])
        rezified_name = _rezify_name(name)

        return _RpmDetails(
            name=rezified_name,
            version=headers["version"],
            os=headers["os"],
            path=path,
            requires=sorted(
                _get_requires(headers["requirename"], headers["requireversion"])
            ),
        )
