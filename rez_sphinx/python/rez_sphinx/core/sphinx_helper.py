"""A collection of functions for making dealing with :ref:`Sphinx` easier."""

import os

_SPHINX_NAME = "conf.py"


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
