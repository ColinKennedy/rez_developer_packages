import argparse

from Qt import QtCore

from ._core import cli_helper, gui


def _parse_arguments(text):
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

    widget = gui.Widget.from_context(namespace.context)
    widget.setWindowTitle("Rez Context GUI")
    widget.setWindowFlags(QtCore.Qt.Window)
    widget.show()
