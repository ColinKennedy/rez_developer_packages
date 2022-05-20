import operator

from rez.utils import formatting
from python_compatibility import graph_node

from . import rez_digraph
from .schemas import node_schema


_ALL_REQUESTS_LABEL = "All Requests"
_ALL_CONFLICTS_LABEL = "All conflicts"


class _RequestRow(graph_node.RowNode):
    def __init__(self, identifier="", parent=None):
        super(_RequestRow, self).__init__(identifier=identifier, parent=parent)

        self._requests = []

    def get_label(self):
        return self._identifier

    def get_requests(self):
        return self._requests

    def set_requests(self, requests):
        self._requests = requests


def _to_label(requests):
    return " ".join([str(request) for request in requests])


def make_conflict_branch(context):
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
    branch = _RequestRow(_ALL_REQUESTS_LABEL)
    branch.set_requests(requests)

    for request in sorted(requests, key=operator.attrgetter("name")):
        child = _RequestRow(_to_label([request]))
        child.set_requests([request])
        branch.append_child(child)

    return branch
