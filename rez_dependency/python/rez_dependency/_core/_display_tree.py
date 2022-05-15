"""A companion module for :mod:`.display_tree`."""

import json
import operator

from . import streamer


def _get_tree_text(tree):
    """Format and return the ``tree`` as text.

    Args:
        tree (dict[str, dict[str, ...]]):
            A recursive dict of dicts containing package tree information.

    Returns:
        str: The formatted output.

    """

    def _get_text(tree, level=0, spacer="    "):
        lines = []

        for key, value in sorted(tree.items(), key=operator.itemgetter(0)):
            if not value:
                lines.append("{indent}{key}".format(indent=level * spacer, key=key))

                continue

            lines.append("{indent}{key}:".format(indent=level * spacer, key=key))
            lines.extend(_get_text(value, level=level + 1, spacer=spacer))

        return lines

    return "\n".join(_get_text(tree))


def as_json(tree):
    """Print ``tree`` as a valid JSON string."""
    streamer.printer(json.dumps(tree, indent=4))


def as_text(tree):
    """Print ``tree`` as compact, human-readable text."""
    streamer.printer(_get_tree_text(tree))
