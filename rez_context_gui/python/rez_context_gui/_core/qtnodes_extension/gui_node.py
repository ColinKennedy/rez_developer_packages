"""Make graph nodes for :mod:`rez_context_gui`."""

import qtnodes
from Qt import QtGui

from . import gui_knob


class Node(qtnodes.Node):
    def __init__(self, header="", parent=None):
        super(Node, self).__init__(parent=parent)

        self.addHeader(qtnodes.Header(node=self, text=header))
        self.addKnob(gui_knob.InputKnob())
        self.addKnob(gui_knob.OutputKnob())

    @classmethod
    def from_contents(cls, contents, *args, **kwargs):
        node = cls(*args, **kwargs)
        node.addHeader(qtnodes.Header(node=node, text=contents.get_label()))
        node.uuid = contents.get_identifier()
        node.fillColor = QtGui.QColor(contents.get_fill_color())

        return node

    def get_label(self):
        if not self.header:
            return ""

        return self.header.text

    def __repr__(self):
        return "{self.__class__.__name__}(header={self.header.text!r}, parent={parent})".format(
            self=self,
            parent=self.parentItem(),
        )
