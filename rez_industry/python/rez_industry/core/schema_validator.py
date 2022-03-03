"""Any function which makes serializing or dealing with Rez schemas easier."""

from rez import package_maker

_SCHEMA_OPTIONS = {
    "tests": package_maker.tests_schema.validate,
}


def serialize(attribute, data):
    """Convert ``attribute`` Rez data into something that's JSON serializable.

    Args:
        attribute (str):
            A Rez attribute attribute. e.g. "tests".
        data (object):
            Anything that you may want to add to `attribute`. If the
            given `attribute` cannot add `data`, ValueError is raised.

    Raises:
        ValueError: If ``atribute`` is not a registered attribute.

    Returns:
        object: The converted, built-in data that is JSON-serializable.

    """
    try:
        caller = _SCHEMA_OPTIONS[attribute]
    except KeyError:
        raise ValueError(
            'attribute "{attribute}" is not currently supported. '
            'The options were, "{options}"'.format(
                attribute=attribute, options=sorted(_SCHEMA_OPTIONS.keys())
            )
        )

    return caller(data)
