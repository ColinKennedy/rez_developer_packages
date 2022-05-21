"""An extended model for :mod:`rez_context_gui` to display Rez requests."""

from Qt import QtCore
from qt_core import node_model


class Model(node_model.SingleRoot):
    """An extended model for :mod:`rez_context_gui` to display Rez requests."""

    node_role = QtCore.Qt.UserRole
    requests_role = QtCore.Qt.UserRole + 1

    def data(self, index, role=QtCore.Qt.DisplayRole):
        """Allow querying the Rez requests from any node in the tree.

        Args:
            index (Qt.QtCore.QModelIndex):
                The row / column / parent Qt location to get some data from.
            role (Qt.QtCore.ItemDataRole):
                A category of data to retrieve within ``index``.

        Returns:
            list[rez.utils.formatting.PackageRequest] or object:
                The found requests or whatever the base class returns.

        """
        if role == self.node_role:
            return index.internalPointer()

        if role == self.requests_role:
            node = index.internalPointer()

            return node.get_requests()

        return super(Model, self).data(index, role)
