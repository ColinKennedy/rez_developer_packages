"""Make running :ref:`rez_sphinx` in unittests easier."""

import os
import contextlib
import sys
import shlex

import six

from rez_utilities import finder
from rez_sphinx import cli


@contextlib.contextmanager
def simulate_resolve(installed_packages):
    """Make a resolve with ``installed_packages`` and :ref:`rez_sphinx`."""
    original_environment = os.environ.copy()
    original_path = sys.path[:]

    for installed_package in installed_packages:
        root = finder.get_package_root(installed_package)
        directory = os.path.join(root, "python")

        if not os.path.isdir(directory):
            raise RuntimeError(
                'Directory "{directory}" does not exist.'.format(directory=directory)
            )

        # TODO : Do a Rez API call here, instead
        os.environ["REZ_{name}_ROOT".format(name=installed_package.name.upper())] = root
        sys.path.append(directory)

    try:
        yield
    finally:
        sys.path = original_path
        os.environ.clear()
        os.environ.update(original_environment)


def test(text):
    """Run ``text`` as if it were run from the terminal.

    Args:
        text (list[str] or str):
            The raw arguments to pass to the "terminal".
            e.g. "build /path/to/directory" or "init".

    """
    parts = text

    if isinstance(parts, six.string_types):
        parts = shlex.split(parts)

    cli.main(parts)
