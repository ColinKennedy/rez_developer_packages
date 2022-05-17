"""The main module for generating GUI components for a Rez resolved context."""

import itertools

import qtnodes
from Qt import QtWidgets

from six.moves import zip

from . import constant, scene_maker, tree_maker
from .qtnodes_extension import gui_node
from .schemas import node_schema


class Widget(QtWidgets.QWidget):
    """The main widget which shows all of the resolves, as graphs.

    The graphs are split based on requested packages and conflicting packages
    so that you can debug and troubleshoot the packages you need, faster.

    """

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


def _from_graph(digraph, parent=None):
    """Convert a pygraph digraph into a nodal widget.

    Args:
        digraph (rez.vendor.pygraph.classes.digraph.digraph):
            The Res resolve, as a :ref:`digraph`.
        parent (:class:`Qt.QtCore.QObject`, optional):
            An object which, if provided, holds a reference to this instance.

    Returns:
        qtnodes.NodeGraphWidget: The generated view of nodes.

    """
    graph = qtnodes.NodeGraphWidget(parent=parent)
    _add_nodes_to_graph(digraph, graph)

    return graph


def _make_gui_trees(context):
    digraph = context.graph()

    # TODO : Update this comment. I think "conflict" might be wrong
    # 1. Make trees
    #
    # - request (all)
    #     - package_a_request-1.2+<2
    #     - package_b_request-2+
    #     - package_c_request<4
    # - conflict (all)
    #     - unresolvable_package-1.2
    #     - another_unresolvable-4+
    #
    request = tree_maker.make_request_branch(context, digraph=digraph)
    conflict = tree_maker.make_conflict_branch(context, digraph=digraph)

    # 2. Now create scenes and views for all tree branches
    request_children = [request] + request.children()
    request_views = scene_maker.make_graphics_view(request_children)
    conflict_children = [conflict] + conflict.children()
    conflict_views = scene_maker.make_graphics_view(conflict_children)

    # 3. Pair each branch with each created view so we can swap view / display later
    request_child_view_pairs = zip(request_children, request_views, strict=True)
    conflict_child_view_pairs = zip(conflict_children, conflict_views, strict=True)

    return list(itertools.chain(request_child_view_pairs, conflict_child_view_pairs))


def from_context(context, parent=None):
    """Convert a Rez context into a node graph.

    Args:
        context (rez.resolved_context.ResolvedContext):
            A successful **or** failing Rez resolve to convert into widgets.
        parent (:class:`Qt.QtCore.QObject`, optional):
            An object which, if provided, holds a reference to this instance.

    Returns:
        Widget: The created widget.

    """
    trees = _make_gui_trees(context)
    widget = Widget(trees, parent=parent)

    return widget
