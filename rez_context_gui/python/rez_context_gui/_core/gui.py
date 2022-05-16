from Qt import QtWidgets

import qtnodes

from . import constant
from .schemas import node_schema
from .qtnodes_extension import gui_node


class Widget(QtWidgets.QWidget):
    def __init__(self, nodes, parent=None):
        super(Widget, self).__init__(parent=parent)

        self._graph = qtnodes.NodeGraphWidget()
        all_types = {type(node) for node in nodes}

        for class_type in all_types:
            self._graph.registerNodeClass(gui_node.Node)

        for node in nodes:
            self._graph.addNode(node)

    @classmethod
    def from_context(cls, context, parent=None):
        digraph = context.graph()

        return cls.from_graph(digraph, parent=parent)

    @classmethod
    def from_graph(cls, digraph, parent=None):
        nodes = _to_nodes(digraph)

        return cls(nodes, parent=parent)


def _to_nodes(digraph):
    nodes = []
    table = dict()

    for node_identifier in digraph.nodes():
        attributes = digraph.node_attributes(node_identifier)
        node_contents = node_schema.Contents.from_rez_graph_attributes(node_identifier, attributes)
        node = gui_node.Node.from_contents(node_contents)
        nodes.append(node)
        table[node_contents.get_identifier()] = node

    for from_node, to_node in digraph.edges():
        source = table[from_node]
        destination = table[to_node]
        source.knob(constant.INPUT_NAME).connectTo(destination.knob(constant.OUTPUT_NAME))

    return nodes
