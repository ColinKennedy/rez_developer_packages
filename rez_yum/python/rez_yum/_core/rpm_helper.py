import collections
import re
import logging
import os

from six import moves

import rpmfile

from . import rpm_require_flag


_LOGGER = logging.getLogger(__name__)
_RpmDetails = collections.namedtuple(
    "_RpmDetails",
    ["name", "os", "path", "requires", "version"],
)
_MODULES = re.compile(r"\([^()]*\)")
_SYMBOLIC_LINK_EXPRESSION = re.compile(r".+\.so(?:(?:\.\d)+)?")


def _is_symbolic_link(name):
    return bool(_SYMBOLIC_LINK_EXPRESSION.match(name))


def _get_requires(headers):
    requires = set()

    for name, version, require_flag in moves.zip(
        headers["requirename"],
        headers["requireversion"],
        headers["requireflags"],
    ):
        if os.path.isabs(name):
            _LOGGER.debug('Skipped: "%s" requirement because it comes from the host OS.', name)

            continue

        stripped = _strip_modules(name)

        if _is_symbolic_link(stripped):
            _LOGGER.debug(
                'Skipped: "%s" requirement because it comes from the host OS.\n'
                'See https://man7.org/linux/man-pages/man7/libc.7.html for details.',
                name,
            )

            continue

        rezified = _rezify_name(stripped)

        if not version:
            requires.add(rezified)

            continue

        try:
            formatted_version = rpm_require_flag.get_require_text(version, require_flag)
        except ValueError:
            print('TODO : fix this bad thing later', (name, version, require_flag))

            continue

        requires.add("{rezified}{formatted_version}".format(rezified=rezified, formatted_version=formatted_version))

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
                _get_requires(headers),
            ),
        )
