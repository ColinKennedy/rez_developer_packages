from python_compatibility import graph_node


class Row(graph_node.RowNode):
    """An example tree node, containing a Rez request."""

    def __init__(self, identifier="", parent=None):
        """Keep track of identifier text + wiget parent.

        Args:
            identifier (str, optional):
                Some text used for debugging, to identify this instance.
            parent (Qt.QtCore.QObject, optional):
                An object which, if provided, holds a reference to this instance.

        """
        super(Row, self).__init__(identifier=identifier, parent=parent)

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


class AllConflictsRow(Row):
    pass


class AllRequestsRow(Row):
    pass
