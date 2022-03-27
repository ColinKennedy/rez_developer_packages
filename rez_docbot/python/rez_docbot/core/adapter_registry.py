import copy
import logging

from .adapters import github


_LOGGER = logging.getLogger(__name__)
_OPTIONS = {"github": github.validate}  # Consider adding more types in the future


def _get_adapter_by_name(name):
    try:
        return _OPTIONS[name]
    except KeyError:
        raise ValueError(
            'Name "{name}" is invalid. Options were, "{options}".'.format(
                name=name, options=sorted(_OPTIONS.keys())
            )
        )


def _validate(item):
    try:
        type_name = item["type"]
    except (TypeError, KeyError, IndexError):
        _LOGGER.exception('Item "%s" could not query the required type.')

        raise

    adapter = _get_adapter_by_name(type_name)

    copied = copy.copy(item)
    del copied["type"]  # Strip the type, we don't need it anymore

    return adapter(copied)


def validate(authentication_methods):
    if not authentication_methods:
        # TODO : Add unittest for this case
        raise ValueError('You must provide at least one authentication method.')

    try:
        iter(authentication_methods)
    except TypeError:
        # If they provide only one authenticator, use that
        # TODO : Add unittest for this case
        return [_validate(authentication_methods)]

    # If there's multiple authentication methods, use those
    # TODO : Add unittest for this case
    return [_validate(item) for item in authentication_methods]
