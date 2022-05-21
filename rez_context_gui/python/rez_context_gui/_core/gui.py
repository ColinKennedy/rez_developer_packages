"""The main module for generating GUI components for a Rez resolved context."""

from python_compatibility import graph_node
from Qt import QtCore, QtWidgets

from . import extended_model, configuration, scene_maker, tree_maker


class Widget(QtWidgets.QWidget):
    """The main widget which shows all of the resolves, as graphs.

    The graphs are split based on requested packages and conflicting packages
    so that you can debug and troubleshoot the packages you need, faster.

    """

    def __init__(self, tree, context, parent=None):
        """Use ``tree`` to select and view one graph at a time, using ``graphs``.

        Args:
            tree (python_compatibility.graph_node.RowNode):
                The top-level root whose **children** will be displayed to the user.
                This class is exclusive - meaning that the top level node
                itself is not shown. Just its children.
            context (rez.resolved_context.ResolvedContext):
                A successful **or** failing Rez resolve to convert into widgets.
            parent (:class:`Qt.QtCore.QObject`, optional):
                An object which, if provided, holds a reference to this instance.

        """
        super(Widget, self).__init__(parent=parent)

        # TODO : Add validation that tree and graphs are compatible
        self.setLayout(QtWidgets.QVBoxLayout())

        self._context = context
        self._digraph = self._context.graph()
        self._index_to_graph = {}

        self._view = QtWidgets.QTreeView()
        self._switcher = QtWidgets.QStackedWidget()
        self._splitter = QtWidgets.QSplitter()

        self._splitter.addWidget(self._view)
        self._splitter.addWidget(self._switcher)
        self.layout().addWidget(self._splitter)

        self._populate_side_bar(tree)

        self._initialize_default_settings()
        self._initialize_interactive_settings()

    def _initialize_default_settings(self):
        """Add all default appearance settings."""
        self._view.expandAll()
        self._view.setHeaderHidden(True)

        self._splitter.setHandleWidth(20)

        for widget, name in [
            (self._splitter, "_splitter"),
            (self._switcher, "_switcher"),
            (self._view, "_view"),
        ]:
            widget.setObjectName(name)

    def _initialize_interactive_settings(self):
        """Change the displayed graph whenever the tree selection changes."""
        self._view.clicked.connect(self._switch_current_graph)

    def _populate_index_graph(self, index):
        """Create a graph for ``index`` and cache + connect the two together.

        Args:
            index (Qt.QtCore.QModelIndex):
                The row / column / parent Qt location to get graph data from.

        Raises:
            RuntimeError: If ``index`` is invalid.

        Returns:
            NodeGraphWidget: The generated or pre-existing graph.

        """
        if not index.isValid():
            raise RuntimeError('Cannot create graph for "{index}".'.format(index=index))

        try:
            return self._index_to_graph[index]
        except KeyError:
            pass

        model = index.model()
        slices = index.data(model.slices_role)
        graph = scene_maker.make_graphics_view(slices, self._digraph)
        self._index_to_graph[index] = graph

        self._switcher.addWidget(graph)

        return graph

    def _populate_side_bar(self, tree):
        """Make a side-bar which displays ``tree``.

        Args:
            tree (python_compatibility.graph_node.RowNode):
                The top-level root whose **children** will be displayed to the user.
                This class is exclusive - meaning that the top level node
                itself is not shown. Just its children.

        """
        model = extended_model.Model(tree)
        self._view.setModel(model)

    def _switch_current_graph(self, index):
        """Make this instance view the graph located at ``index``.

        Args:
            index (Qt.QtCore.QModelIndex):
                The row / column / parent Qt location to get some data from.

        """
        graph = self._populate_index_graph(QtCore.QPersistentModelIndex(index))

        self._switcher.setCurrentWidget(graph)

    def set_configuration(self, configuration):
        model = self._view.model()
        root = model.index(0, 0, QtCore.QModelIndex())
        index = configuration.get_default_index(root)
        self._switch_current_graph(index)


def _clear_stacked(widget):
    """Remove all widgets from a stacked ``widget``.

    Args:
        widget (Qt.QtWidgets.QStackedWidget): The object to completely clear.

    """
    for index in reversed(range(widget.count())):
        widget.removeWidget(widget.widget(index))


def _make_gui_trees(context):
    """Create all trees and graphs for ``context``.

    Args:
        context (rez.resolved_context.ResolvedContext):
            A successful **or** failing Rez resolve to convert into widgets.

    Returns:
        tuple[python_compatibility.graph_node.RowNode, dict[str, NodeGraphWidget]]:
            Each node which is meant to be displayed as a tree index and the
            graph that should be displayed whenever that tree index is later
            selected.

    """
    request = tree_maker.make_request_branch(context.requested_packages())
    # TODO : Ensure that ``conflict`` only shows a label if there's no actual conflict.
    conflict = tree_maker.make_conflict_branch(context)

    root = graph_node.RowNode(identifier="root")
    root.append_child(request)
    root.append_child(conflict)

    return root


def _to_hashable(request):
    """frozenset[rez.utils.formatting.PackageRequest]: All Rez package requests."""
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
    tree = _make_gui_trees(context)
    widget = Widget(tree, context, parent=parent)
    widget.set_configuration(configuration.Configuration.create_new())

    return widget
