"""A small interface for querying Rez :ref:`digraph` data."""

from . import _attribute


class Contents(object):
    """A small interface for querying Rez :ref:`digraph` data."""

    def __init__(self, identifier, data):
        """Store a node by ID and its attributes.

        Args:
            identifier (str):
                Some UUID to represent this instance. From Rez, it's usually a
                string like ``"_1"``, ``"_17"``, etc.
            data (dict[str, object]):
                Each attribute name and value which describes this instance.

        """
        super(Contents, self).__init__()

        self._identifier = identifier
        self._data = data

    @classmethod
    def from_rez_graph_attributes(cls, identifier, attributes):
        """Validate and convert ``attributes`` and make a new instance.

        .. code-block:: python

            digraph = context.graph()  # context is a rez.resolved_context.ResolvedContext

            for node_identifier in digraph.nodes():
                attributes = digraph.node_attributes(node_identifier)
                node = Contents.from_rez_graph_attributes(node_identifier, attributes)

        Args:
            identifier (str):
                Some UUID to represent this instance. From Rez, it's usually a
                string like ``"_1"``, ``"_17"``, etc.
            attributes (iter[tuple[str, object]]):
                Each attribute name and value which describes this instance.

        Returns:
            Contents: The generated instance.

        """
        data = dict()

        for name, value in attributes:
            validator = _attribute.get_from_name(name)
            data[name] = validator(value)

        return cls(identifier, data)

    def get_identifier(self):
        """str: Some UUID to represent this instance."""
        return self._identifier

    def get_label(self):
        """str: A human-readable phrase that is displayed in GUIs."""
        return self._data[_attribute.LABEL]

    def get_fill_color(self):
        """str: The hex background color for this GUI node, e.g. ``"#111111"``."""
        return self._data[_attribute.FILL_COLOR]

    def get_font_size(self):
        """int: A 1-or-more value representing how big the label should be."""
        return self._data[_attribute.FONT_SIZE]
