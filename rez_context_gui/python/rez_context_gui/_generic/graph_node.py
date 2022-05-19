_ROW_NOT_FOUND = -1


class RowNode(object):
    def __init__(self, identifier="", parent=None):
        super(RowNode, self).__init__()

        self._children = []
        self._identifier = identifier
        self._parent = None

        if parent:
            parent.append_child(self)

    def find_child(self, node):
        try:
            return self._children.index(node)
        except ValueError:
            raise RuntimeError(
                'Node "{node!r}" could not be found in "{self!r}".'.format(
                    node=node, self=self
                )
            )

    def get_child(self, row):
        return self._children[row]

    def get_child_count(self):
        # TODO : Possible optimization point
        return len(self._children)

    def get_children(self):
        return self._children

    def get_column_count(self):
        # TODO : Add note on why, here
        return 1

    def get_identifier(self):
        return self._identifier

    def get_parent(self):
        return self._parent

    def get_row(self):
        if not self._parent:
            return _ROW_NOT_FOUND

        return self._parent.find_child(self)

    def append_child(self, node):
        node.set_parent(self)
        self._children.append(node)

    def set_parent(self, node):
        self._parent = node

    def __repr__(self):
        return "{self.__class__.__name__}(identifier={self._identifier!r}, parent={parent})".format(
            self=self, parent=self.get_parent(),
        )
