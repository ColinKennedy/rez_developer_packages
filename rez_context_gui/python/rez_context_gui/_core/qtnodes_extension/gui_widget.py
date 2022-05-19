from Qt import QtWidgets

from qtnodes import edge as edge_
import qtnodes


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
                for edge in knob.edges:
                    knob_of_hidden_node = edge.target
                    hidden_neighbor_node = knob_of_hidden_node.parentItem()
                    hidden_neighbor_node.show()
                    expanded = True
                    edge.show()

                # raise ValueError(knob.edges)
                # if not isinstance(knob, qtnodes.OutputKnob):
                #     continue
                #
                # for edge in self._get_edges_from_output_knob(knob):
                #     hidden_neighbor_node = edge.target
                #     hidden_neighbor_node.show()
                #     edge.show()
                #
                #     expanded = True

        if expanded:
            return

        QtWidgets.QMessageBox.information(
            self,
            "Nothing To Expand",
            "You've reached the end of the graph. There's nothing new to show.",
        )

    def _expand_to_non_conflict(self):
        # TODO : Add support for this method
        raise NotImplementedError("Need to write")

    def _get_edges_from_output_knob(self, knob):
        for item in self.scene.items():
            print('ITEM', item)
            if isinstance(item, edge_.Edge):
                print('SOURCE', item.source, knob)

        return [
            item
            for item in self.scene.items()
            if isinstance(item, edge_.Edge) and item.source == knob
        ]

    def _get_selected_nodes(self):
        return [
            item
            for item in self.scene.selectedItems()
            if isinstance(item, qtnodes.Node)
        ]
