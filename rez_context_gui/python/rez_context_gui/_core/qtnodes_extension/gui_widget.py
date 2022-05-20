import qtnodes
from Qt import QtWidgets


class NodeGraphWidget(qtnodes.NodeGraphWidget):
    def contextMenuEvent(self, event):
        """Show a menu to create registered Nodes."""
        menu = QtWidgets.QMenu(self)
        action = menu.addAction("Expand Selection")
        action.triggered.connect(self._expand_selection)
        # TODO : Hide unless it's actually within a conflict
        action = menu.addAction("Expand To Non-Conflict")
        action.triggered.connect(self._expand_to_non_conflict)

        menu.exec_(event.globalPos())

    def _expand_selection(self):
        def _get_node_to_show(knob_of_hidden_node):
            neighbor_node = knob_of_hidden_node.parentItem()

            if neighbor_node.isVisible():
                return None

            return neighbor_node

        def _show_upstream(knob):
            shown = False

            for edge in knob.edges:
                neighbor_node = _get_node_to_show(edge.source)

                if neighbor_node:
                    neighbor_node.show()
                    edge.show()
                    shown = True

            return shown

        def _show_downstream(knob):
            shown = False

            for edge in knob.edges:
                neighbor_node = _get_node_to_show(edge.target)

                if neighbor_node:
                    neighbor_node.show()
                    edge.show()
                    shown = True

            return shown

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
                local_expanded = _show_downstream(knob)

                if local_expanded:
                    expanded = True

                    continue

                local_expanded = _show_upstream(knob)

                if local_expanded:
                    expanded = True

        if expanded:
            return

        QtWidgets.QMessageBox.information(
            self,
            "Nothing To Expand",
            "You've already expanded this node. Try a different node selection!",
        )

    def _expand_to_non_conflict(self):
        # TODO : Add support for this method
        raise NotImplementedError("Need to write")

    def _get_selected_nodes(self):
        return [
            item
            for item in self.scene.selectedItems()
            if isinstance(item, qtnodes.Node)
        ]
