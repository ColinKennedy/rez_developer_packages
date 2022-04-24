import argparse
import os

from rez.cli import _complete_util


def add_directory_argument(parser):
    """Make ``parser`` include a positional argument pointing to a file path on-disk.

    Args:
        parser (argparse.ArgumentParser): The instance to modify.

    """
    parser.add_argument(
        "directory",
        nargs="?",
        default=os.getcwd(),
        help="The folder to search for a Rez package. "
        "Defaults to the current working directory.",
    )


def add_remainder_argument(parser):
    """Tell ``parser`` to collect all text into a single namespace parameter.

    Args:
        parser (argparse.ArgumentParser):
            The parser to extend with the new parameter.

    """
    remainder = parser.add_argument(
        "remainder",
        nargs="*",
        help=argparse.SUPPRESS,
    )
    remainder.completer = _complete_util.SequencedCompleter(
        "remainder",
        _complete_util.ExecutablesCompleter,
        _complete_util.FilesCompleter(),
    )
