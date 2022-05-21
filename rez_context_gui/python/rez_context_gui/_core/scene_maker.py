"""Create Qt scene + view + widgets.

This module takes a Rez digraph, makes a :class:`Qt.QtWidgets.QGraphicsScene`,
and populates it with nodes that are shown / hidden by default.

"""

from qtnodes import edge as edge_
from qtnodes import layout
from qtnodes import node as node_

from . import constant
from .qtnodes_extension import gui_node, gui_widget
from .schemas import node_schema


def _add_nodes_to_graph(digraph, graph):
    """Add all nodes and edges within ``digraph`` into a node ``graph``.

    Args:
        digraph (rez.vendor.pygraph.classes.digraph.digraph):
            The Res resolve, as a :ref:`digraph`.
        graph (qtnodes.NodeGraphWidget):
            The view to create and append nodes into.

    """
    nodes = []
    table = {}

    # 1. Create initial nodes
    for node_identifier in digraph.nodes():
        attributes = digraph.node_attributes(node_identifier)
        node_contents = node_schema.Contents.from_rez_graph_attributes(
            node_identifier, attributes
        )
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
        source.knob(constant.INPUT_NAME).connectTo(
            destination.knob(constant.OUTPUT_NAME)
        )


def make_graphics_view(requests, digraph):
    """Create a Qt node scene + view + widget for ``requests``, using ``digraph``.

    Args:
        requests (set[str]):
            Each Rez package request from some context to generate a Qt scene from.
        digraph (rez.vendor.pygraph.classes.digraph.digraph):
            The visual representation of the nodes + edges of some Rez resolve.

    Returns:
        NodeGraphWidget: The generated scene, pre-populated with nodes.

    """
    graph = gui_widget.NodeGraphWidget()
    _add_nodes_to_graph(digraph, graph)
    # TODO : For some reason when I layout the scene, the "python" request
    # is just gone. Need to fix this
    #
    layout.autoLayout(graph.scene)

    for item in graph.scene.items():
        if isinstance(item, node_.Node):
            item.setVisible(item.get_label() in requests)

            continue

        if isinstance(item, edge_.Edge):
            knob = item.target
            parent_node = knob.node()
            item.setVisible(parent_node.get_label() in requests)

            continue

    return graph
