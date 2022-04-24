import schema
import six


def validate_list_of_str_or_str(item):
    if not item:
        return []

    if isinstance(item, six.string_types):
        return [item]

    return schema.Schema([str]).validate(item)
