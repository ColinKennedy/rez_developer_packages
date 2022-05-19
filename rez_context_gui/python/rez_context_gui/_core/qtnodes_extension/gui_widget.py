from Qt import QtWidgets

import qtnodes


class NodeGraphWidget(qtnodes.NodeGraphWidget):
    def contextMenuEvent(self, event):
        """Show a menu to create registered Nodes."""
        menu = QtWidgets.QMenu(self)
        action = menu.addAction("Expand Selection")
        action.triggered.connect(self._expand_selection)
        action = menu.addAction("Expand To Non-Conflict")
        action.triggered.connect(self._expand_to_non_conflict)

        menu.exec_(event.globalPos())

    def _expand_selection(self):
        for node in self.scene.selectedItems():
            for knob in node.knobs():
                if isinstance(knob, qtnodes.OutputKnob):
                    node = self.getNodeById(knob.target.uuid)
                    node.show()

    def _expand_to_non_conflict(self):
        # TODO : Add support for this method
        raise NotImplementedError('Need to write')
