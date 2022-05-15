"""The main module for formatting text for the :ref:`list sub-command`."""


def get_lines(tree):
    """Get every unique package name from ``tree``.

    Args:
        tree (dict[str, dict[str, ...]]):
            A recursive dict of dicts containing package tree information.

    Returns:
        list[str]: Each found Rez package family name.

    """

    def _recurse(tree, packages):
        for key, value in tree.items():
            packages.add(key)

            _recurse(value, packages)

    packages = set()
    _recurse(tree, packages)

    return sorted(packages)
