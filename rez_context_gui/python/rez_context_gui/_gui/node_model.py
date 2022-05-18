from Qt import QtCore


class SingleRoot(QtCore.QAbstractItemModel):
    # Reference: https://gist.github.com/nbassler/342fc56c42df27239fa5276b79fca8e6

    def __init__(self, root, parent=None):
        super(SingleRoot, self).__init__(parent=parent)

        self._root = root

    def columnCount(self, parent=QtCore.QModelIndex()):
        if not parent.isValid():
            return self._root.get_column_count()

        return parent.internalPointer().get_column_count()

    def data(self, index, role=QtCore.Qt.DisplayRole):
        if not index.isValid():
            return None

        node = index.internalPointer()

        if role == QtCore.Qt.DisplayRole:
            return node.get_identifier()

        return None

    def index(self, row, column, parent=QtCore.QModelIndex()):
        if not parent.isValid():
            parent_node = self._root
        else:
            parent_node = parent.internalPointer()

        try:
            child = parent_node.get_child(row)
        except IndexError:
            # Under normal circumstances this should never be possible. However
            # if the user manually calls ``index()`` for any reason with the
            # wrong row / column, this situation may occur.
            #
            return QtCore.QModelIndex()

        return self.createIndex(row, column, child)

    def parent(self, child):
        if not child.isValid():
            return QtCore.QModelIndex()

        parent = child.internalPointer().get_parent()

        if not parent:
            return QtCore.QModelIndex()

        return self.createIndex(parent.get_row(), 0, parent)

    def rowCount(self, index):
        if not index.isValid():
            return self._root.get_child_count()

        return index.internalPointer().get_child_count()
