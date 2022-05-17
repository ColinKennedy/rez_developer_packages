import qtnodes

from Qt import QtGui

from . import gui_knob


class Node(qtnodes.Node):
    def __init__(self, header="", *args, **kwargs):
        super(Node, self).__init__(*args, **kwargs)

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
