import operator

from .._generic import graph_node


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
    # TODO : Add support for this later
    print(sorted(item for item in dir(context) if "graph" in item.lower()))
    raise ValueError(context.graph_)


def make_request_branch(requests):
    branch = _RequestRow("All requests")
    branch.set_requests(requests)

    for request in sorted(requests, key=operator.attrgetter("name")):
        child = _RequestRow(_to_label([request]))
        child.set_requests([request])
        branch.append_child(child)

    return branch
