import logging
import sys

from Qt import QtWidgets

from . import cli


_LOGGER = logging.getLogger("rez_context_gui")
_HANDLER = logging.StreamHandler(sys.stdout)
_HANDLER.setLevel(logging.INFO)
_FORMATTER = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
_HANDLER.setFormatter(_FORMATTER)
_LOGGER.addHandler(_HANDLER)
_LOGGER.setLevel(logging.INFO)

_APPLICATION = QtWidgets.QApplication([])

cli.main(sys.argv[1:])

_APPLICATION.exec_()
