from Qt import QtWidgets

import qtnodes

from . import constant
from .schemas import node_schema
from .qtnodes_extension import gui_node


class Widget(QtWidgets.QWidget):
    def __init__(self, graph, parent=None):
        super(Widget, self).__init__(parent=parent)

        # TODO : Remove this later, since it appears to be unnecessary
        self.setLayout(QtWidgets.QVBoxLayout())
        self.layout().addWidget(graph)

    @classmethod
    def from_context(cls, context, parent=None):
        digraph = context.graph()

        return cls.from_graph(digraph, parent=parent)

    @classmethod
    def from_graph(cls, digraph, parent=None):
        graph = qtnodes.NodeGraphWidget()
        _add_nodes_to_graph(digraph, graph)

        return cls(graph, parent=parent)


def _add_nodes_to_graph(digraph, graph):
    nodes = []
    table = dict()

    # 1. Create initial nodes
    for node_identifier in digraph.nodes():
        attributes = digraph.node_attributes(node_identifier)
        node_contents = node_schema.Contents.from_rez_graph_attributes(node_identifier, attributes)
        node = gui_node.Node.from_contents(node_contents)
        graph.scene.addItem(node)
        table[node_contents.get_identifier()] = node

    # 2. Register node types
    all_types = {type(node) for node in nodes}

    for class_type in all_types:
        graph.registerNodeClass(class_type)

    # 3. Assign knob connections for all of the nodes
    for from_node, to_node in digraph.edges():
        source = table[from_node]
        destination = table[to_node]
        source.knob(constant.INPUT_NAME).connectTo(destination.knob(constant.OUTPUT_NAME))


def _from_graph(digraph, parent=None):
    graph = qtnodes.NodeGraphWidget(parent=parent)
    # _add_nodes_to_graph(digraph, graph)

    return graph


def from_context(context, parent=None):
    digraph = context.graph()

    return _from_graph(digraph, parent=parent)
