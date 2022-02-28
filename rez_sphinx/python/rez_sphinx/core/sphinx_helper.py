"""A collection of functions for making dealing with :ref:`Sphinx` easier."""

import os

_SPHINX_NAME = "conf.py"


def _get_indent(text):
    """str: Get the whitespace text leading up to ``text``."""
    return text[: len(text) - len(text.lstrip())]


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


def is_empty_toctree(lines):
    """Check if ``lines`` has no existing entries.

    Args:
        lines (iter[str]):
            Some toctree text. 
            e.g. ``[".. toctree::", "   :maxdepth: 2"]`` would return True.
            e.g. ``[".. toctree::", "   :maxdepth: 2", "", "   something"]``
            would return False.

    Returns:
        bool: If ``lines`` describes an empty :ref:`toctree`, return True.

    """
    for line in lines:
        if not _get_indent(line):
            continue

        if line.strip().startswith(":"):
            continue

        return True

    return False


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


def get_toctree_indent(lines):
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

    return trees
