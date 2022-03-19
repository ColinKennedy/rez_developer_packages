"""Dealing with :class:`schema.Optional` objects."""

import logging

from six.moves import collections_abc
import schema as schema_
import six

from . import generic


_LOGGER = logging.getLogger(__name__)


def _get_non_default_values(data, optional):
    """Get every non-default value within ``data``.

    Args:
        data (object):
            An iterable array, map, or non-iterable object to consider.
        optional (:class:`schema.Optional`):
            A schema-aware type which contextualizes ``data``. It should
            contain what the "known default" value should be if ``data`` has
            undefined parts.

    Raises:
        RuntimeError: If nothing was set to a non-default value.

    Returns:
        :class:`schema.Optional` or dict or list:

    """
    if not has_default(optional):
        return data

    if data == optional.default:
        raise RuntimeError("Nothing was changed.")

    if not generic.is_iterable(optional.default) or isinstance(
        optional.default, six.string_types
    ):
        return data
    elif not isinstance(optional.default, collections_abc.MutableMapping):
        return data

    new = optional.default.__class__()

    for key, default_value in optional.default.items():
        if isinstance(key, schema_.Optional):
            raw_key = _get_raw_key(key)

            try:
                new[raw_key] = _get_non_default_values(data[raw_key], key)
            except RuntimeError:
                continue

        recorded_value = data[key]

        if recorded_value == default_value:
            _LOGGER.debug('Key "%s" has the same value, "%s". Skipping.', key, default_value)

            continue

        new[key] = recorded_value

    return new


def _get_raw_key(key):
    """Reduce any potential schema object to its builtin, hashable Python object.

    Args:
        key (:class:`schema.Optional` or object):
            Any schema object is converted. Any built-in is ignored.

    Returns:
        object: (Usually this is a ``str``) - The converted object.

    """
    if not hasattr(key, "key"):
        return key

    return key.key


def _get_real_key(key, schema):
    """Find a matching schema key from a raw, data ``key``.

    Args:
        key (str): An example dict key to check within ``schema``.
        schema (:class:`schema.Schema`):
            A description of the required and optional data.

    Returns:
        :class:`schema.Optional` or NoneType: The found key or nothing.

    """
    for real_key in schema._schema.keys():
        if not isinstance(real_key, schema_.Optional):
            continue

        if real_key.key == key:
            return real_key

    return None


def has_default(optional):
    """Check if ``optional`` has a default value assigned.

    Args:
        optional (:class:`schema.Optional`): The object to consider.

    Returns:
        bool: If there's a default, return True.

    """
    return hasattr(optional, "default")


def serialize_sparsely(settings, schema):
    """Strip all default values from ``settings``, using ``schema``.

    Args:
        settings (dict):
            The base, raw data to traverse and return.
        schema (:class:`schema.Schema`):
            A description of the required and optional data.

    Returns:
        dict: The stripped, non-default data.

    """
    output = dict()

    for key, data in settings.items():
        real_key = _get_real_key(key, schema)

        if not real_key:
            output[key] = data

            continue

        try:
            output[key] = _get_non_default_values(data, real_key)
        except RuntimeError:
            continue

    return output
