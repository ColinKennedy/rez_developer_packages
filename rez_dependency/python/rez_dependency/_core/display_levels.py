"""The main module for formatting text for the :ref:`levels sub-command`."""

import collections
import operator


def get_lines(tree):
    """Convert ``tree`` into a list of package levels.

    Args:
        tree (dict[str, dict[str, ...]]):
            A recursive dict of dicts containing package tree information.

    Returns:
        list[str]: The formatted text.

    """

    def _get(tree, banks, level=0):
        for key, value in tree.items():
            banks[level].add(key)

            _get(value, banks, level=level + 1)

    banks = collections.defaultdict(set)
    _get(tree, banks)
    lines = []

    for level, packages in sorted(banks.items(), key=operator.itemgetter(0)):
        lines.append(
            "#{level}: {packages}".format(
                level=level, packages=" ".join(sorted(packages))
            )
        )

    return lines
