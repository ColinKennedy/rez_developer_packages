import schema

from qt_core import iterbot
from . import tree_row


_CONFLICTS_FALLBACK_KEY = "conflicts_then_requests"
_CONFLICTS_KEY = "conflicts"
_REQUESTS_KEY = "requests"


def _get_conflicts(tree):
    raise ValueError(tree)


def _get_conflicts_then_requests(tree):
    raise ValueError(tree)


def _get_by_type(tree, class_type):
    role = tree.model().node_role

    for index in iterbot.iter_child_indices(tree):
        if isinstance(index.data(role), class_type):
            return index

    raise RuntimeError("No requests row could be found.")


def _get_conflicts(tree):
    return _get_by_type(tree, tree_row.AllConflictsRow)


def _get_requests(tree):
    return _get_by_type(tree, tree_row.AllRequestsRow)


def _validate_conflicts_selection(value):
    if value != _CONFLICTS_KEY:
        raise ValueError('Value "{value}" is not "{_CONFLICTS_KEY}".'.format(value=value, _CONFLICTS_KEY=_CONFLICTS_KEY))

    return _get_conflicts


def _validate_conflicts_then_requests_selection(value):
    if value != _CONFLICTS_KEY:
        raise ValueError('Value "{value}" is not "{_CONFLICTS_FALLBACK_KEY}".'.format(value=value, _CONFLICTS_FALLBACK_KEY=_CONFLICTS_FALLBACK_KEY))

    return _get_conflicts_then_requests


def _validate_requests_selection(value):
    if value != _REQUESTS_KEY:
        raise ValueError('Value "{value}" is not "{_REQUESTS_KEY}".'.format(value=value, _REQUESTS_KEY=_REQUESTS_KEY))

    return _get_requests


SELECTION = schema.Or(
    schema.Use(_validate_requests_selection),
    schema.Use(_validate_conflicts_selection),
)
DEFAULT_SELECTION = lambda: _get_requests
