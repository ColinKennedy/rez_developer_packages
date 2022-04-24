import argparse
import os

from rez.cli import _complete_util


class _SplitPaths(argparse.Action):
    r"""Parse a user CLI argument which is "path separated".

    e.g. In Linux, it'd split ``"/foo:/bar"`` into ``["/foo", "/bar"]``.
    e.g. In Windows, it'd split ``"C:\foo;C:\bar"`` into ``["C:\foo", "C:\bar"]``.

    """

    def __call__(self, parser, namespace, values, option_string=None):
        setattr(namespace, self.dest, [value.strip() for value in values.split(os.pathsep)])


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


def add_packages_path_argument(parser):
    """Allow ``parser`` to specify the folders where installed Rez packages live.

    Args:
        parser (argparse.ArgumentParser):
            The parser to extend with the new parameter.

    """
    parser.add_argument("--packages-path", default=[], action=_SplitPaths)


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
