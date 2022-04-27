"""Generic schema-check related functions."""

import schema
import six


def validate_list_of_str_or_str(item):
    """Conform a string to a list-of-strings.

    Args:
        item (list[str] or str): Incoming, raw data to conform.

    Returns:
        list[str]: The found items, if any.

    """
    if not item:
        return []

    if isinstance(item, six.string_types):
        return [item]

    return schema.Schema([str]).validate(item)
