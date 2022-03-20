"""A simple module for dealing with printing in different text formats."""

from __future__ import print_function

import pprint

import yaml


def _print_python(data):
    """Print ``data``, raw, to the terminal."""
    try:
        pprint.pprint(
            data, indent=4, sort_dicts=True
        )  # pylint: disable=unexpected-keyword-arg
    except TypeError:
        # `sort_keys` is only in later Python versions. Starting somewhere around
        # Python 3.7+
        pprint.pprint(data, indent=4)


def _print_yaml(data):
    """Convert ``data`` to `yaml`_, then print."""
    print(yaml.dump(data, sort_keys=True))


PYTHON_FORMAT = "python"
CHOICES = {PYTHON_FORMAT: _print_python, "yaml": _print_yaml}


def get_format_caller(key):
    """Find an appropriate printer, using ``key``.

    Args:
        key (str): An identifier like "python", "yaml", etc. See :attr:`CHOICES`.

    Raises:
        ValueError: If ``key`` has no found result.

    Returns:
        callable[object]:
            A function which takes on parameter and prints to the terminal.

    """
    try:
        return CHOICES[key]
    except KeyError:
        raise ValueError(
            'Key "{key}" not valid. Options were, "{options}".'.format(
                key=key,
                options=sorted(CHOICES.keys()),
            )
        )
