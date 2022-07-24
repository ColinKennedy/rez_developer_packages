"""Any classes / functions to make using :mod:`argparse` easier."""

import argparse
import fnmatch
import functools
import os


class GlobList(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        output = []

        for value in values:
            output.append(functools.partial(_glob_match, value))

        setattr(namespace, self.dest, output)


class SplitPaths(argparse.Action):
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
        setattr(
            namespace, self.dest, [value.strip() for value in values.split(os.pathsep)]
        )


def _glob_match(pattern, text):
    return fnmatch.fnmatch(text, pattern)
