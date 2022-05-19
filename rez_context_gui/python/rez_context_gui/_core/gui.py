"""The main module for generating GUI components for a Rez resolved context."""

from Qt import QtWidgets

from python_compatibility import graph_node, zipper
from . import extended_model, scene_maker, tree_maker


class Widget(QtWidgets.QWidget):
    """The main widget which shows all of the resolves, as graphs.

    The graphs are split based on requested packages and conflicting packages
    so that you can debug and troubleshoot the packages you need, faster.

    """

    def __init__(self, tree, graphs, parent=None):
        """Use ``tree`` to select and view one graph at a time, using ``graphs``.

        Args:
            tree (python_compatibility.graph_node.RowNode):
                The top-level root whose **children** will be displayed to the user.
                This class is exclusive - meaning that the top level node
                itself is not shown. Just its children.
            graphs (dict[frozenset[rez.utils.formatting.PackageRequest], NodeGraphWidget]):
                Each set of nodes to display. For each branch / leaf in ``tree``,
                there should be a corresponding entry in ``graphs``.
            parent (:class:`Qt.QtCore.QObject`, optional):
                An object which, if provided, holds a reference to this instance.

        """
        super(Widget, self).__init__(parent=parent)

        # TODO : Add validation that tree and graphs are compatible
        self.setLayout(QtWidgets.QVBoxLayout())

        self._node_to_graph = {}

        self._view = QtWidgets.QTreeView()
        self._switcher = QtWidgets.QStackedWidget()
        self._splitter = QtWidgets.QSplitter()

        self._splitter.addWidget(self._view)
        self._splitter.addWidget(self._switcher)
        self.layout().addWidget(self._splitter)

        self._populate_side_bar(tree)
        self._populate_graphs(graphs)

        self._initialize_default_settings()
        self._initialize_interactive_settings()

    def _initialize_default_settings(self):
        for widget, name in [
            (self._splitter, "_splitter"),
            (self._switcher, "_switcher"),
            (self._view, "_view"),
        ]:
            widget.setObjectName(name)

    def _initialize_interactive_settings(self):
        """Change the displayed graph whenever the tree selection changes."""
        self._view.clicked.connect(self._switch_current_graph)

    def _populate_graphs(self, graphs):
        # TODO : Add docstrings
        _clear_stacked(self._switcher)

        self._node_to_graph = graphs

        for graph in graphs.values():
            self._switcher.addWidget(graph)

    def _populate_side_bar(self, tree):
        model = extended_model.Model(tree)
        self._view.setModel(model)

    def _switch_current_graph(self, index):
        model = index.model()
        request = index.data(model.request_role)
        graph = self._node_to_graph[_to_hashable(request)]

        self._switcher.setCurrentWidget(graph)


def _clear_stacked(widget):
    for index in reversed(range(widget.count())):
        widget.removeWidget(widget.widget(index))


def _make_gui_trees(context):
    digraph = context.graph()

    request = tree_maker.make_request_branch(context.requested_packages())
    request_children = [request] + request.get_children()
    request_views = scene_maker.make_graphics_view(request_children, digraph)
    request_child_view_pairs = zipper.zip_equal(request_children, request_views)

    root = graph_node.RowNode(identifier="root")
    root.append_child(request)

    request_graph_map = {_to_hashable(node.get_requests()): graph for node, graph in request_child_view_pairs}

    return root, request_graph_map

    # TODO : Finish this later
    # # TODO : Update this comment. I think "conflict" might be wrong
    # # 1. Make trees
    # #
    # # - request (all)
    # #     - package_a_request-1.2+<2
    # #     - package_b_request-2+
    # #     - package_c_request<4
    # # - conflict (all)
    # #     - unresolvable_package-1.2
    # #     - another_unresolvable-4+
    # #
    # request = tree_maker.make_request_branch(context.requested_packages())
    # conflict = tree_maker.make_conflict_branch(context)
    #
    # # 2. Now create scenes and views for all tree branches
    # request_children = [request] + request.children()
    # request_views = scene_maker.make_graphics_view(request_children)
    # conflict_children = [conflict] + conflict.children()
    # conflict_views = scene_maker.make_graphics_view(conflict_children)
    #
    # # 3. Pair each branch with each created view so we can swap view / display later
    # request_child_view_pairs = zip(request_children, request_views, strict=True)
    # conflict_child_view_pairs = zip(conflict_children, conflict_views, strict=True)
    #
    # return list(itertools.chain(request_child_view_pairs, conflict_child_view_pairs))


def _to_hashable(request):
    return frozenset(request)


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
    tree, graphs = _make_gui_trees(context)
    widget = Widget(tree, graphs, parent=parent)

    return widget
