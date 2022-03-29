"""A module for collecting all adapter modules / classes into one place."""

import copy
import logging

from six.moves import collections_abc

from .github import github

_LOGGER = logging.getLogger(__name__)
_OPTIONS = {"github": github.validate}  # Consider adding more types in the future


def _get_adapter_by_name(name):
    """Get an adapter using ``name``.

    Args:
        name (str): A known adapter type. e.g. ``"github"``.

    Raises:
        ValueError: If ``name`` doesn't match a known adapter.

    Returns:
        TODO Fix this

    """
    try:
        return _OPTIONS[name]
    except KeyError:
        raise ValueError(
            'Name "{name}" is invalid. Options were, "{options}".'.format(
                name=name, options=sorted(_OPTIONS.keys())
            )
        )


def _validate(item):
    """Convert ``item`` and its contents into an adapter.

    Args:
        item (dict[str, object]): All details needed to construct an adapter.

    Returns:
        TODO : Write here once the type / content is known.

    """
    try:
        type_name = item["type"]
    except (TypeError, KeyError, IndexError):
        _LOGGER.exception('Item "%s" could not query the required type.', item)

        raise

    adapter = _get_adapter_by_name(type_name)

    copied = copy.copy(item)
    del copied["type"]  # Strip the type, we don't need it anymore

    return adapter(copied)


def validate(authentication_methods):
    """Convert ``authentication_methods`` and its contents into adapters.

    Args:
        authentication_methods (list[dict[str, object]] or dict[str, object]):
            A collection of adapter data. Or just a single adapter.

    Raises:
        ValueError: If ``authentication_methods`` is empty.

    Returns:
        list[TODO]: All generated adapters.

    """
    if not authentication_methods:
        # TODO : Add unittest for this case
        raise ValueError("You must provide at least one authentication method.")

    if isinstance(authentication_methods, collections_abc.Mapping):
        # If they provide only one authenticator, use that
        # TODO : Add unittest for this case
        return [_validate(authentication_methods)]

    # If there's multiple authentication methods, use those
    # TODO : Add unittest for this case
    return [_validate(item) for item in authentication_methods]
