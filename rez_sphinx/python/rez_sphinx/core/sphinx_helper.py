"""A collection of functions for making dealing with :ref:`Sphinx` easier."""

import textwrap
import logging
import os

_LOGGER = logging.getLogger(__name__)
_SPHINX_NAME = "conf.py"
_MISSING_TOCTREE_TEMPLATE = (".. toctree::", "   :max-depth: 1")


def _get_indent(text):
    """str: Get the whitespace text leading up to ``text``."""
    return text[: len(text) - len(text.lstrip())]


def _get_toctree_entries(lines):
    """Check if ``lines`` has no existing entries.

    Args:
        lines (iter[str]):
            Some toctree text.
            e.g. ``[".. toctree::", "   :maxdepth: 2"]`` would return ``[]``.
            e.g. ``[".. toctree::", "   :maxdepth: 2", "", "   something"]``
            would return ``["something"]``.

    Returns:
        list[str]: Each .rst reference within the ``lines`` toctree.

    """
    entries = []

    for line in lines:
        if not _get_indent(line):
            continue

        if line.strip().startswith(":"):
            continue

        entries.append(line.strip())

    return entries


def _get_toctree_indent(lines):
    """Get the inner text indentation of a :ref:`toctree`, using ``lines``.

    Args:
        lines (iter[str]):
            Some toctree text.
            e.g. ``[".. toctree::", "   :maxdepth: 2"]`` would return "   ".
            e.g. ``[".. toctree::", "    :maxdepth: 2"]`` would return "    ".

    Raises:
        RuntimeError: If no indentation could be found.

    Returns:
        str: The found indentation.

    """
    for line in lines:
        indent = _get_indent(line)

        if indent:
            return indent

    raise RuntimeError('Lines "{lines}" has no indentation.'.format(lines=lines))


def _get_toctree_insert_index(text, entries):
    for index, entry in enumerate(entries):
        if text > entry:
            return index - 1

    return len(entries) - 1


def _add_link_to_a_tree(toctree_line, trees, data):
    """Find the appropriate :ref:`toctree` to add ``line`` onto.

    Args:
        toctree_line (str): The API documentation line to append.
        trees (list[list[str]]): Each found toctree.
        data (str): The blob of text which ``trees`` are a part of.

    Raises:
        RuntimeError: If ``trees`` already contains ``toctree_line`` at least once.

    Returns:
        str: The newly modified ``data``, which now includes ``line``.

    """
    for tree in trees:
        _, _, lines = tree

        for line in lines:
            if line == toctree_line.strip():
                _LOGGER.debug(
                    'Link already added in tree "%s". Skipping.',
                    tree,
                )

                raise RuntimeError(
                    'Link "{toctree_line}" already exists.'.format(toctree_line=toctree_line)
                )

    tree = trees[0]
    start_line, end_line, tree_lines = tree

    lines = data.splitlines()
    indent = _get_toctree_indent(lines)

    print('RTEE LINES', tree_lines)
    entries = _get_toctree_entries(tree_lines)
    print('EBNTRIES', tree_lines)

    # Find a good, alphabetical position to include ``toctree_line`` into ``tree``
    index = _get_toctree_insert_index(toctree_line, entries)
    position = end_line - index - 1

    lines.insert(position, indent + toctree_line)
    trees[0] = start_line, len(lines), lines

    return "\n".join(lines)


def _make_new_tree(entries=tuple()):
    indent = _get_indent(_MISSING_TOCTREE_TEMPLATE[-1])
    lines = list(_MISSING_TOCTREE_TEMPLATE) + [indent + line for line in entries]

    return "\n".join(lines)


def _scan_for_configuration_path(directory):
    """Recursively look for the :ref:`Sphinx conf.py` or fail trying.

    Args:
        directory (str):
            A path on-disk to search within for the :ref:`Sphinx conf.py <conf.py>`.

    Raises:
        RuntimeError: If no :ref:`Sphinx conf.py <conf.py>` could be found.

    Returns:
        str: The path on-disk to the :ref:`Sphinx conf.py <conf.py>`.

    """
    for root, _, files in os.walk(directory):
        for name in files:
            if name == _SPHINX_NAME:
                return os.path.join(root, name)

    raise RuntimeError(
        'Directory "{directory}" has no inner conf.py file.'.format(directory=directory)
    )


def find_configuration_path(root):
    """Find the :ref:`Sphinx conf.py` or fail trying.

    Args:
        root (str):
            A directory on-disk to search within for the
            :ref:`Sphinx conf.py <conf.py>`.

    Returns:
        str: The path on-disk to the :ref:`Sphinx conf.py <conf.py>`.

    """
    for path in (
        os.path.join(root, "source", _SPHINX_NAME),  # rez-sphinx's default location
        os.path.join(root, _SPHINX_NAME),  # Another common, non-default spot
    ):
        if os.path.isfile(path):
            return path

    return _scan_for_configuration_path(root)


def get_toctrees(data):
    """Get every :ref:`toctree` in ``path``.

    Args:
        path (str): The absolute or relative path to a Sphinx .rst file.

    Returns:
        list[tuple[int, int, list[str]]]: Each :ref:`toctree` as a list of lines.

    """

    def _trim(tree):
        count = 0

        for index in reversed(range(len(tree))):
            if tree[index].strip():
                break

            count += 1

        return tree[: -1 * count]

    start = -1
    trees = []
    current = []
    last_indent = ""

    for index, line in enumerate(data.splitlines()):
        if line.startswith(".. toctree::"):
            start = index
            current.append(line)

            continue

        if start == -1:
            continue

        if not line.strip():
            current.append(line)

            continue

        indent = _get_indent(line)

        if indent < last_indent:
            last_indent = ""
            trimmed = _trim(current)
            end = start + len(trimmed)
            trees.append((start, end, trimmed))
            current = []
            start = -1
        else:
            last_indent = indent
            current.append(line)
    else:
        if current:
            last_indent = ""
            trimmed = _trim(current)
            end = start + len(trimmed)
            trees.append((start, end, trimmed))
            current = []
            start = -1

    return trees


def add_links_to_a_tree(entries, path):
    with open(path, "r") as handler:
        data = handler.read()

    trees = get_toctrees(data)

    if not trees:
        new_data = _make_new_tree(entries=entries)

        with open(path, "w") as handler:
            handler.write(new_data)

        return

    original = data

    for text in entries:
        try:
            data = _add_link_to_a_tree(text, trees, data)
        except RuntimeError:
            continue

    if data == original:
        _LOGGER.info('Skipped writing to path "%s" because no changes were made.', path)

        return

    with open(path, "w") as handler:
        handler.write(data)
