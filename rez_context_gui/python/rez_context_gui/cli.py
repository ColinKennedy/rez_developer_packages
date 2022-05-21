"""A module for parsing and running some CLI action."""

import argparse

from Qt import QtCore, QtWidgets

from ._core import cli_helper, gui


def _parse_arguments(text):
    """Convert raw user-provided text into Python objects.

    Args:
        text (list[str]): The space-separated information to parse.

    Returns:
        argparse.Namespace: The parsed arguments.

    """
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "context",
        action=cli_helper.ContextFile,
        help="The saved context.rxt on-disk to load as a GUI.",
    )

    return parser.parse_args(text)


def main(text):
    """Parse the user's arguments and show a GUI."""
    namespace = _parse_arguments(text)

    application = QtWidgets.QApplication([])

    widget = gui.from_context(namespace.context)
    widget.setWindowTitle("Rez Context GUI")
    widget.setWindowFlags(QtCore.Qt.Window)
    widget.show()

    application.exec_()
