import copy
import logging

from .adapters import github


_LOGGER = logging.getLogger(__name__)
_OPTIONS = {"github": github.Adapter}  # Consider adding more types in the future


def _get_adapter_by_name(name):
    try:
        return _OPTIONS[name]
    except KeyError:
        raise ValueError(
            'Name "{name}" is invalid. Options were, "{options}".'.format(
                name=name, options=sorted(_OPTIONS.keys())
            )
        )


def validate(item):
    try:
        type_name = item["type"]
    except (TypeError, KeyError, IndexError):
        _LOGGER.exception('Item "%s" could not query the required type.')

        raise

    adapter = _get_adapter_by_name(type_name)

    copied = copy.copy(item)
    del copied["type"]  # Strip the type, we don't need it anymore
    authenticated = adapter.validate(copied)

    return authenicated
