from qtnodes import edge as edge_, node as node_
from qtnodes import layout

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


def make_graphics_view(request_rows, digraph):
    graphs = []

    for row in request_rows:
        graph = gui_widget.NodeGraphWidget()
        _add_nodes_to_graph(digraph, graph)
        # TODO : For some reason when I layout the scene, the "python" request
        # is just gone. Need to fix this
        #
        layout.autoLayout(graph.scene)

        requests = {str(request) for request in row.get_requests()}

        for item in graph.scene.items():
            if isinstance(item, node_.Node):
                item.setVisible(item.get_label() in requests)

                continue

            if isinstance(item, edge_.Edge):
                knob = item.target
                parent_node = knob.node()
                item.setVisible(parent_node.get_label() in requests)

                continue

        graphs.append(graph)

    return graphs
