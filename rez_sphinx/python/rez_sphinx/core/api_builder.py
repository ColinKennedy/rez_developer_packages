"""A module for handling API Python .rst Sphinx files.

This module has strong tie-ins with :ref:`sphinx.ext.autodoc`. Read that
documentation for mode details.

"""

import collections

_Mode = collections.namedtuple("_Mode", "label, description")

FULL_AUTO = _Mode(
    "full-auto",
    "completely automatically generate API Python .rst files on-build.",
)
GENERATE = _Mode(
    "generate", "The same as full-auto but the files are copied here.",
)

NONE = _Mode("none", "Don't generate API .rst files at all.")

MODES = (FULL_AUTO, GENERATE, NONE)
