"""Make nodes that the GUI can then display as connected graphs."""

import operator

from rez.utils import formatting
from python_compatibility import graph_node

from . import rez_digraph
from .schemas import node_schema


_ALL_REQUESTS_LABEL = "All Requests"
_ALL_CONFLICTS_LABEL = "All conflicts"


class _RequestRow(graph_node.RowNode):
    """An example tree node, containing a Rez request."""

    def __init__(self, identifier="", parent=None):
        """Keep track of identifier text + wiget parent.

        Args:
            identifier (str, optional):
                Some text used for debugging, to identify this instance.
            parent (Qt.QtCore.QObject, optional):
                An object which, if provided, holds a reference to this instance.

        """
        super(_RequestRow, self).__init__(identifier=identifier, parent=parent)

        self._requests = []

    def get_label(self):
        """str: The text to display in a GUI."""
        return self._identifier

    def get_requests(self):
        """list[rez.utils.formatting.PackageRequest]: Each individual Rez package."""
        return self._requests

    def set_requests(self, requests):
        """Keep track of Rez :ref:`packages <package>` to graph and display.

        Args:
            requests (list[rez.utils.formatting.PackageRequest]):
                Each individual Rez package to track for this tree node instance.

        """
        self._requests = requests


def _to_label(requests):
    """str: Convert Rez package requests into a simple display."""
    return " ".join([str(request) for request in requests])


def make_conflict_branch(context):
    """Make a tree of nodes, indicating some conflict.

    Args:
        context (rez.resolved_context.ResolvedContext):
            The falied Rez context to convert into a tree of conflict nodes.

    Returns:
        _RequestRow:
            The created node tree and all of its conflict branches.
            It's pretty commont for this tree to only have a single branch / leaf.

    """
    def _get_conflicting_nodes(digraph):
        nodes = []
        flattened = []

        for node_edges in digraph.edges():
            if not rez_digraph.is_conflict_edge(digraph.edge_attributes(node_edges)):
                continue

            nodes.append(node_edges)
            flattened.extend(node_edges)

        return nodes, flattened

    def _to_flattened_requests(nodes, digraph):
        output = []

        for digraph_node in nodes:
            output.append(_to_request_from_node(digraph_node, digraph))

        return output

    def _to_request_from_node(digraph_node, dirgraph):
        graph_node = node_schema.Contents.from_rez_graph_attributes(
            digraph_node,
            digraph.node_attributes(digraph_node),
        )

        return formatting.PackageRequest(graph_node.get_label())

    digraph = context.graph()

    nodes, flattened = _get_conflicting_nodes(digraph)
    branch = _RequestRow(_ALL_CONFLICTS_LABEL)
    requests = _to_flattened_requests(flattened, digraph)
    branch.set_requests(requests)

    for source, destination in nodes:
        requests = [
            _to_request_from_node(source, digraph),
            _to_request_from_node(destination, digraph),
        ]
        child = _RequestRow(_to_label(requests))
        child.set_requests(requests)
        branch.append_child(child)

    return branch


def make_request_branch(requests):
    """Make a tree of nodes, indicating some raw Rez requests.

    Args:
        requests (list[rez.utils.formatting.PackageRequest]):
            Each individual Rez package to track for this tree node instance.

    Returns:
        _RequestRow:
            The created node tree with each of its requests as individual node
            branches. This tree can end up having a lot of leaves, if you use
            a lot of requests.

    """
    branch = _RequestRow(_ALL_REQUESTS_LABEL)
    branch.set_requests(requests)

    for request in sorted(requests, key=operator.attrgetter("name")):
        child = _RequestRow(_to_label([request]))
        child.set_requests([request])
        branch.append_child(child)

    return branch
