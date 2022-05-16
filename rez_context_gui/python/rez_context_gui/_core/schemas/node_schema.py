import schema

from . import _attribute


_LABEL = "label"
_SCHEMA = schema.Schema(
    [
        schema.Or(
            _attribute.FILL_COLOR,
        )
    ]
)


class Contents(object):
    def __init__(self, identifier, data):
        super(Contents, self).__init__()

        self._identifier = identifier
        self._data = data

    @classmethod
    def from_rez_graph_attributes(cls, identifier, attributes):
        data = dict()

        for name, value in attributes:
            validator = _attribute.get_from_name(name)
            data[name] = validator(value)

        return cls(identifier, data)

    def get_identifier(self):
        return self._identifier

    def get_label(self):
        return self._data[_attribute.LABEL]

    def get_fill_color(self):
        return self._data[_attribute.FILL_COLOR]

    def get_font_size(self):
        return self._data[_attribute.FONT_SIZE]
