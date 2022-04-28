"""All tests for :mod:`qt_rez_core`."""

import six
from Qt import QtWidgets

_APPLICATION = QtWidgets.QApplication([])  # Don't remove this. It allows tests to run

six.add_move(six.MovedModule("mock", "mock", "unittest.mock"))
