from Qt import QtCore
from qt_core import node_model


class Model(node_model.SingleRoot):
    request_role = QtCore.Qt.UserRole

    def data(self, index, role=QtCore.Qt.DisplayRole):
        if role == self.request_role:
            node = index.internalPointer()

            return node.get_requests()

        return super(Model, self).data(index, role)
