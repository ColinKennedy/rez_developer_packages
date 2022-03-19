import schema as schema_

from . import generic


def _get_key(key, schema):
    for real_key in schema._schema.keys():
        if not isinstance(real_key, schema_.Optional):
            continue

        if real_key.key == key:
            return real_key

    return None


def _get_non_default_values(data, optional):
    if not has_default(optional):
        return data

    if data == optional.default:
        raise RuntimeError("Nothing was changed.")

    if not generic.is_iterable(optional.default):
        return data
    elif not _is_dict(optional.default):
        return data

    raise ValueError("Keep going here")

    new = optional.default.__class__()

    for key, value in optional.default.items():
        new[key] = _get_non_default_values(data, key)


def has_default(optional):
    return hasattr(optional, "default")


def serialize_sparsely(settings, schema):
    output = dict()

    for key, data in settings.items():
        real_key = _get_key(key, schema)

        if not real_key:
            output[key] = data

            continue

        try:
            output[real_key] = _get_non_default_values(data, real_key)
        except RuntimeError:
            continue

    return output
