"""Extra classes and functions to make :mod:`.cli` easier to write."""

import argparse
import os

from rez.config import config
from rez.utils import formatting

from . import display_tree, exception


class _SplitPaths(argparse.Action):  # pylint: disable=too-few-public-methods
    """A parser action which splits path strings by ":" / ";"."""

    def __call__(self, parser, namespace, values, option_string=None):
        """Add the split paths onto ``namespace``.

        Args:
            parser (argparse.ArgumentParser):
                The current parser that this instance is applied onto.
            namespace (argparse.Namespace):
                The destination where parsed values are placed onto.
            values (str):
                Raw user input content to split and add to the parser.
            option_string (str, optional):
                The flag from the CLI. e.g. :ref:`--packages-path`.

        """
        # Strip each path, just in case there's unneeded whitespace
        paths = []

        for value in values.split(os.pathsep):
            value = value.strip()

            if value:
                paths.append(value)

        setattr(namespace, self.dest, paths)


class _ValidateRequest(argparse.Action):  # pylint: disable=too-few-public-methods
    """Ensure that only Rez package family is specified at a time."""

    def __call__(self, parser, namespace, values, option_string=None):
        """Make sure ``values`` doesn't have more than one Rez package specified.

        Args:
            parser (argparse.ArgumentParser):
                The current parser that this instance is applied onto.
            namespace (argparse.Namespace):
                The destination where parsed values are placed onto.
            values (list[str]):
                Raw user input content to split and add to the parser.
            option_string (str, optional):
                The flag from the CLI.

        Raises:
            UserInputError:
                If ``values`` has 2-or-more requests which point to the same
                Rez package family.

        """
        seen = set()
        invalids = set()

        for text in values:
            request = formatting.PackageRequest(text)
            name = request.name

            if name in seen:
                invalids.add(name)

                continue

            seen.add(name)

        if not invalids:
            setattr(namespace, self.dest, values)

            return

        raise exception.UserInputError(
            'Packages "{invalids}" were requested more than once. '
            "Please re-try with only a single request per-family.".format(
                invalids=sorted(invalids)
            )
        )


class SelectDisplayer(argparse.Action):  # pylint: disable=too-few-public-methods
    """Choose a callable display function, from :mod:`.display_tree`."""

    def __call__(self, parser, namespace, values, option_string=None):
        """Choose a callable display function, from :mod:`.display_tree`.

        Args:
            parser (argparse.ArgumentParser):
                The current parser that this instance is applied onto.
            namespace (argparse.Namespace):
                The destination where parsed values are placed onto.
            values (str):
                Raw user input content to split and add to the parser.
            option_string (str, optional):
                The flag from the CLI. e.g. :ref:`--display-as`.

        """
        caller = display_tree.get_option(values)

        setattr(namespace, self.dest, caller)


def add_build_requires_parameter(parser):
    """Add :ref:`--build-requires` to ``parser``.

    Args:
        parser (argparse.ArgumentParser):
            Some command / sub-command to directly modify.

    """
    parser.add_argument(
        "--build-requires",
        action="store_true",
        help="If included, `build_requires` dependencies are also checked.",
    )


def add_packages_path_parameter(parser):
    """Add :ref:`--packages-path` to ``parser``.

    Args:
        parser (argparse.ArgumentParser):
            Some command / sub-command to directly modify.

    """
    parser.add_argument(
        "--packages-path",
        action=_SplitPaths,
        default=config.packages_path,  # pylint: disable=no-member
        help="The folders on-disk to look for Rez packages.",
    )

    return parser


def add_private_build_requires_parameter(parser):
    """Add :ref:`--private-build-requires` to ``parser``.

    Args:
        parser (argparse.ArgumentParser):
            Some command / sub-command to directly modify.

    """
    parser.add_argument(
        "--private-build-requires",
        action="store_true",
        help="If included, `private_build_requires` dependencies are also checked.",
    )


def add_request_parameter(parser):
    """Describe a series of Rez package(s) to later convert into a Rez context.

    This could contain a single package request or multiple.

    Args:
        parser (argparse.ArgumentParser):
            Some command / sub-command to directly modify.

    """
    parser.add_argument(
        "request",
        action=_ValidateRequest,
        nargs="+",
        help="All packages to query from. e.g. ``foo-1 bar-2+``.",
    )
