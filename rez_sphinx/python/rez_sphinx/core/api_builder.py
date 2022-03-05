"""A module for handling API Python .rst Sphinx files.

This module has strong tie-ins with :ref:`sphinx.ext.autodoc`. Read that
documentation for mode details.

"""

import collections

from . import _api_builder

_Mode = collections.namedtuple("_Mode", "label, description, execute")
# Reference: https://stackoverflow.com/a/18348004/3626104
_Mode.__new__.__defaults__ = (None,)


FULL_AUTO = _Mode(
    "full-auto",
    "completely automatically generate API Python .rst files on-build.",
    _api_builder.generate_api_files,
)

NONE = _Mode("none", "Don't generate API .rst files at all.")

MODES = (FULL_AUTO, NONE)


def get_from_label(label):
    """Convert ``label`` into :obj:`_Mode`.

    Args:
        label (str):
            The name of some API .rst mode to convert. e.g. "full-auto",
            "generate", "none", etc.

    Raises:
        ValueError: If ``label`` doesn't match a mode.

    Returns:
        :obj:`_Mode`: The found mode.

    """
    for mode in MODES:
        if label == mode.label:
            return mode

    raise ValueError(
        'Label "{label}" is not a model. Options were, "{options}".'.format(
            label=label, options=sorted(mode.label for mode in MODES)
        )
    )
