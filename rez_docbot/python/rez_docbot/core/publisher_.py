"""The main class which handles creating and publishing to git repositories."""

from ..publishers import publisher_registry

_PUBLISHER_KEY = "publisher"


def validate_publisher(package, data):
    try:
        type_ = data[_PUBLISHER_KEY]
    except TypeError:
        raise ValueError('Expected a dict but got "{data}".'.format(data=data))

    data = {key: value for key, value in data.items() if key != _PUBLISHER_KEY}
    publisher_class = publisher_registry.get_by_name(type_)

    return publisher_class.validate(data, package)
