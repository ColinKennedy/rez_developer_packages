import qtnodes
from Qt import QtWidgets


class NodeGraphWidget(qtnodes.NodeGraphWidget):
    def contextMenuEvent(self, event):
        """Show a menu to create registered Nodes."""
        menu = QtWidgets.QMenu(self)
        selection_actions = menu.addSeparator()
        selection_actions.setText("Selection Actions")
        menu.addAction(selection_actions)
        action = menu.addAction("Expand Downstream")
        action.triggered.connect(self._expand_selection_downstream)
        action = menu.addAction("Expand Upstream")
        action.triggered.connect(self._expand_selection_upstream)

        menu.exec_(event.globalPos())

    def _expand_selection_downstream(self):
        def _show_downstream(knob):
            shown = False

            for edge in knob.edges:
                neighbor_node = _get_node_to_show(edge.target)

                if neighbor_node:
                    neighbor_node.show()
                    edge.show()
                    shown = True

            return shown

        self._expand_selection(_show_downstream)

    def _expand_selection_upstream(self):
        def _show_upstream(knob):
            shown = False

            for edge in knob.edges:
                neighbor_node = _get_node_to_show(edge.source)

                if neighbor_node:
                    neighbor_node.show()
                    edge.show()
                    shown = True

            return shown

        self._expand_selection(_show_upstream)

    def _expand_selection(self, caller):
        selection = self._get_selected_nodes()

        if not selection:
            QtWidgets.QMessageBox.warning(
                self,
                "No Selection",
                "Please select any node and try again.",
            )

            return

        expanded = False

        for node in selection:
            for knob in node.knobs():
                local_expanded = caller(knob)

                if local_expanded:
                    expanded = True

        if expanded:
            return

        QtWidgets.QMessageBox.information(
            self,
            "Nothing To Expand",
            "You've already expanded this node. Try a different node selection!",
        )

    def _get_selected_nodes(self):
        return [
            item
            for item in self.scene.selectedItems()
            if isinstance(item, qtnodes.Node)
        ]


def _get_node_to_show(knob):
    """Find the hidden node of ``knob``.

    Args:
        knob (InputKnob or OutputKnob): Some knob to check for.

    Returns:
        Node or None:
            The knob's node, if the node is hidden. Otherwise, return nothing.

    """
    neighbor_node = knob.parentItem()

    if neighbor_node.isVisible():
        return None

    return neighbor_node
