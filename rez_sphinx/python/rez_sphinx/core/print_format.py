"""A simple module for dealing with printing in different text formats."""

from __future__ import print_function

import pprint

import yaml

PYTHON_FORMAT = "python"


def _print_python(data):
    """Print ``data``, raw, to the terminal."""
    try:
        pprint.pprint(  # pylint: disable=unexpected-keyword-arg
            data, indent=4, sort_dicts=True  # `sort_dicts` is Python 3.8+
        )
    except TypeError:
        # `sort_keys` is only in later Python versions. Starting somewhere around
        # Python 3.7+
        pprint.pprint(data, indent=4)


def _print_yaml(data):
    """Convert ``data`` to `yaml`_, then print."""
    print(yaml.dump(data, sort_keys=True))


def get_choices():
    """dict[str, callable[str]]: Each allowed print format and its print function."""
    return {PYTHON_FORMAT: _print_python, "yaml": _print_yaml}


def get_format_caller(key):
    """Find an appropriate printer, using ``key``.

    Args:
        key (str): An identifier like "python", "yaml", etc. See :attr:`choices`.

    Raises:
        ValueError: If ``key`` has no found result.

    Returns:
        callable[object]:
            A function which takes on parameter and prints to the terminal.

    """
    choices = get_choices()

    try:
        return choices[key]
    except KeyError:
        raise ValueError(
            'Key "{key}" not valid. Options were, "{options}".'.format(
                key=key,
                options=sorted(choices.keys()),
            )
        )