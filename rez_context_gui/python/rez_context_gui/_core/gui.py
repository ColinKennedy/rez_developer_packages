from Qt import QtWidgets


class Widget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(Widget, self).__init__(parent=parent)

    @classmethod
    def from_context(cls, context, parent=None):
        graph = context.graph()

        return cls.from_graph(graph, parent=parent)

    @classmethod
    def from_graph(cls, graph, parent=None):
        nodes = []

        for node in graph.nodes:
            nodes.append(Node.from_digraph_node(node))

        for edge in graph.edges:
            raise ValueError()
            nodes.connect

        return cls(nodes, parent=parent)
