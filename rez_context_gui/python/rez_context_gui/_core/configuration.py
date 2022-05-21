import schema
from rez.config import config

from . import _configuration


_MASTER_KEY = "rez_context_gui"
_DEFAULT_SELECTION = "default_selection"
_SCHEMA = schema.Schema(
    {
        schema.Optional(
            _DEFAULT_SELECTION,
            default=_configuration.DEFAULT_SELECTION,
        ): _configuration.SELECTION,
    }
)


class Configuration(object):
    def __init__(self, data):
        super(Configuration, self).__init__()

        self._data = data

    @classmethod
    def create_new(cls, data=None):
        data = data or config.optionvars.get(_MASTER_KEY, {})
        validated = _SCHEMA.validate(data)

        return cls(validated)

    def get_default_index(self, index):
        caller = self._data[_DEFAULT_SELECTION]

        return caller(index)
