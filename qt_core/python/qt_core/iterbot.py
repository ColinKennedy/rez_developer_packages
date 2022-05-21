"""Helper functions to make iterating over Qt objects easier.

These functions are meant to be as generic as possible.

"""

import itertools


def _iter_model_indices(index, model):
    """Traverse all model for indices, starting at ``index``.

    - This is a DFS (depth first search) traversal
    - Is **inclusive** (``index`` is the first yielded result).
    - Iterates rows first, then columns.

    Args:
        index (Qt.QtCore.QModelIndex):
            The index to start searching for child indices, if any.
        model (Qt.QtCore.QAbstractItemModel):
            The source location of ``index``.

    Yields:
        Qt.QtCore.QModelIndex: Each found index.

    """
    yield index

    for row, column in itertools.product(
        range(model.rowCount(index)), range(model.columnCount(index))
    ):
        child = model.index(row, column, parent=index)

        for grand_child in _iter_model_indices(child, model):
            yield grand_child


def iter_child_indices(index):
    """Traverse all indices on-and-under ``index``.

    - This is a DFS (depth first search) traversal
    - Is **inclusive** (root-level indices are included & yielded).
    - Iterates rows first, then columns.

    Args:
        index (Qt.QtCore.QModelIndex): A index to check for chiindices.

    Yields:
        Qt.QtCore.QModelIndex: Each found index.

    """
    model = index.model()

    for child in _iter_model_indices(index, model):
        yield child
