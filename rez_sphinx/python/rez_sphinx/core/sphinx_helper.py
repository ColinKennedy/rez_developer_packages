"""A collection of functions for making dealing with `Sphinx`_ easier."""

import logging
import os

from . import doc_finder, exception

_LOGGER = logging.getLogger(__name__)
_SPHINX_NAME = "conf.py"
_MISSING_TOCTREE_TEMPLATE = (".. toctree::", "   :max-depth: 1")


def _is_empty(lines):
    """Check if ``lines`` has no existing entries.

    Args:
        lines (iter[str]):
            Some toctree text.
            e.g. ``[".. toctree::", "   :maxdepth: 2"]`` would return True.
            e.g. ``[".. toctree::", "   :maxdepth: 2", "", "   something"]``
            would return False.

    Returns:
        bool: If ``lines`` toctree has an existing entries.

    """
    for line in lines:
        if not _get_indent(line):
            continue

        if line.strip().startswith(":"):
            continue

        return False

    return True


def _get_indent(text):
    """str: Get the whitespace text leading up to ``text``."""
    return text[: len(text) - len(text.lstrip())]


def _get_toctree_indent(lines):
    """Get the inner text indentation of a `toctree`_, using ``lines``.

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


def _add_links_to_a_tree(entries, tree, data):
    """Find the appropriate `toctree`_ to add ``line`` onto.

    Args:
        entries (list[str]): The documentation line to append to in ``tree``.
        tree (list[str]): The toctree to modify.
        data (str): The blob of text which ``trees`` are a part of.

    Raises:
        RuntimeError: If ``tree`` already contains ``toctree_line`` at least once.

    Returns:
        str: The newly modified ``data``, which now includes ``line``.

    """
    _, end_line, tree_lines = tree

    lines = data.splitlines()
    indent = _get_toctree_indent(tree_lines)

    if _is_empty(tree_lines):
        position = end_line + 1
    else:
        position = end_line

    for line in reversed(entries):
        lines.insert(position, indent + line)

    return "\n".join(lines)


def _make_new_tree(entries=tuple()):
    """Make a brand new toctree, using ``entries``.

    Args:
        entries (list[str]): The documentation line to append to in ``trees`` later.

    Returns:
        str: The blob of toctree text.

    """
    indent = _get_indent(_MISSING_TOCTREE_TEMPLATE[-1])
    lines = list(_MISSING_TOCTREE_TEMPLATE) + [indent + line for line in entries]

    return "\n".join(lines)


def _scan_for_configuration_path(directory):
    """Recursively look for the `Sphinx conf.py`_ or fail trying.

    Args:
        directory (str):
            A path on-disk to search within for the `conf.py <Sphinx conf.py>`_.

    Raises:
        RuntimeError: If no `conf.py <Sphinx conf.py>`_ could be found.

    Returns:
        str: The path on-disk to the `conf.py <Sphinx conf.py>`_.

    """
    for root, _, files in os.walk(directory):
        for name in files:
            if name == _SPHINX_NAME:
                return os.path.join(root, name)

    raise RuntimeError(
        'Directory "{directory}" has no inner conf.py file.'.format(directory=directory)
    )


def _skip_existing_entries(entries, trees):
    """Filter out ``entries`` if any exist in any of ``trees``.

    Args:
        entries (list[str]): The documentation line to append to in ``trees`` later.
        trees (list[list[str]]): Each toctree and its lines to search within.

    Returns:
        list[str]: The ``entries`` which don't already exist in ``trees``.

    """
    tree_lines = set()

    for tree in trees:
        _, _, lines = tree

        for line in lines:
            tree_lines.add(line.strip())

    output = []

    for entry in entries:
        if entry not in tree_lines:
            output.append(entry)

            continue

        _LOGGER.debug('Link "%s" already added in an existing tree. Skipping.', entry)

    return output


def find_configuration_path(root):
    """Find the `Sphinx conf.py`_ or fail trying.

    Args:
        root (str):
            A directory on-disk to search within for the `conf.py <Sphinx conf.py>`_.

    Returns:
        str: The path on-disk to the `conf.py <Sphinx conf.py>`_.

    """
    try:
        source = doc_finder.get_source_from_directory(root)
    except exception.NoDocumentationFound:
        _LOGGER.warning('Directory "%s" has no documentation.', root)

        return ""

    path = os.path.join(source, _SPHINX_NAME)

    if os.path.isfile(path):
        return path

    return _scan_for_configuration_path(root)


def get_toctrees(data):
    """Get every `toctree`_ in ``path``.

    Args:
        path (str): The absolute or relative path to a Sphinx .rst file.

    Returns:
        list[tuple[int, int, list[str]]]: Each `toctree`_ as a list of lines.

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

    if current:
        last_indent = ""
        trimmed = _trim(current)
        end = start + len(trimmed)
        trees.append((start, end, trimmed))
        current = []
        start = -1

    return trees


def add_links_to_a_tree(entries, path):
    """Add ``entries`` as line items within a toctree in ``path``.

    If ``path`` doesn't have at least one toctree defined, a new one will be
    created and then ``entries`` is added to that.

    Note:
        If ``entries`` are already in ``path``, this function does nothing.
        Otherwise, ``path`` will be directly modified.

    Todo:
        - Make sure adding a brand-new tree works
        - Make sure skipping works

    Args:
        entries (list[str]): The documentation line to append to ``path``.
        path (str): An absolute or relative file path to some ReST file.

    """
    with open(path, "r") as handler:
        data = handler.read()

    trees = get_toctrees(data)

    if not trees:
        new_data = _make_new_tree(entries=entries)

        with open(path, "w") as handler:
            handler.write(new_data)

        return

    original = data
    entries = _skip_existing_entries(entries, trees)

    if not entries:
        _LOGGER.info('Path "%s" already has every Entry, "%s".', path, entries)

        return

    tree = trees[0]
    data = _add_links_to_a_tree(entries, tree, data)

    if data == original:
        _LOGGER.info('Skipped writing to path "%s" because no changes were made.', path)

        return

    with open(path, "w") as handler:
        handler.write(data)


def htmlize_ref(path, text):
    """Convert ``text`` to its HTML equivalent. Attach it to ``path``.

    Args:
        path (str): The relative or absolute path to a HTML page. e.g. "page.html".
        text (str): A raw string which represents a HTML anchor label. e.g. "Some Thing".

    Returns:
        str: The converted HTML link. e.g. "page.html#some-thing".

    """
    # TODO : Make this function cleaner, later. Preferably call whatever Sphinx calls
    htmlized = text.replace(" ", "-").lower()

    return "{path}#{htmlized}".format(path=path, htmlized=htmlized)
