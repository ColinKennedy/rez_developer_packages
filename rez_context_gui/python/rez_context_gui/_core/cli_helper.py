"""Any class / function that makes writing :mod:`argparse` CLIs a bit easier."""

import argparse
import os

from rez import resolved_context

from . import exception


class ContextFile(argparse.Action):  # pylint: disable=too-few-public-methods
    """Ensure that only Rez package family is specified at a time."""

    def __call__(self, parser, namespace, values, option_string=None):
        """Convert a context file path into a Rez context.

        Args:
            parser (argparse.ArgumentParser):
                The current parser that this instance is applied onto.
            namespace (argparse.Namespace):
                The destination where parsed values are placed onto.
            values (str):
                An absolute or relative path on-disk to a context file.
            option_string (str, optional):
                The flag from the CLI.

        Raises:
            InvalidContext: If the found context could not resolve.

        """
        path = os.path.normpath(os.path.expanduser(os.path.expanduser(values)))

        context = _get_context(path)

        if context.success:
            setattr(namespace, self.dest, context)

            return

        raise exception.InvalidContext(
            'Path "{path}" is an invalid context.'.format(path=path)
        )


def _get_context(path):
    """Convert ``path`` into a Rez context.

    Args:
        path (str):
            The relative to absolute path to a context .rxt file on-disk.  If
            the path is relative, the ``$PWD`` is used to resolve it to an
            absolute path.

    Raises:
        ContextNotFound:
            If ``path`` is a relative path and no actual Rez context file can
            be found.

    Returns:
        rez.resolved_context.ResolvedContext: The resolve from ``path``.

    """
    if os.path.isabs(path):
        return resolved_context.ResolvedContext.load(path)

    current_directory = os.getcwd()
    resolved = os.path.join(current_directory, path)

    if not os.path.isfile(resolved):
        raise exception.ContextNotFound(
            'Path "{path}" does not point to a Rez context file.'.format(
                path=path
            )
        )

    return resolved_context.ResolvedContext.load(path)
