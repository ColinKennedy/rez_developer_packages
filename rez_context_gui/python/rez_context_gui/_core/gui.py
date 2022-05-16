from Qt import QtWidgets

from .schemas import node_schema


class Widget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(Widget, self).__init__(parent=parent)

    @classmethod
    def from_context(cls, context, parent=None):
        graph = context.graph()

        return cls.from_graph(graph, parent=parent)

    @classmethod
    def from_graph(cls, graph, parent=None):
        nodes = _to_nodes(graph)

        return cls(nodes, parent=parent)


def _to_nodes(graph):
    nodes = []
    table = dict()

    for node_identifier in graph.nodes():
        attributes = graph.node_attributes(node_identifier)
        node_contents = node_schema.Contents.from_rez_graph_attributes(node_identifier, attributes)

        nodes.append(Node.from_digraph_node(node))
        table[node_contents.get_identifier()] = node_contents

    for from_node, to_node in graph.edges():
        source = table[from_node]
        destination = table[to_node]
        raise ValueError(source, destination)

    return nodes
