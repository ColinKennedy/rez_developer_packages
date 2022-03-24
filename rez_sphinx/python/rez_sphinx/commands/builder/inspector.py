import logging
import operator

from rez_utilities import finder

from ...core import configuration, doc_finder, exception

_LOGGER = logging.getLogger(__name__)


def _get_all_field_attributes(sphinx):
    attributes = sphinx.get_module_attributes()

    if attributes:
        return attributes

    path = sphinx.get_module_path()

    raise exception.SphinxConfError(
        'Configuration "{path}" has no found attributes.'.format(path=path)
    )


def _get_field_attributes(sphinx, fields):
    attributes = {name: value for name, value in sphinx.get_module_attributes().items()}
    _LOGGER.debug(
        'Found conf.py attributes, "%s". From file, "%s"',
        ", ".join(sorted(attributes.keys())),
        sphinx.get_module_path(),
    )

    invalids = set()
    output = []

    for name in fields:
        if name not in attributes:
            invalids.add(name)
        else:
            output.append((name, attributes[name]))

    if not invalids:
        return output

    if len(fields) == 1:
        raise exception.SphinxConfError(
            'This conf.py attribute, "{invalids}" could not be found.'.format(
                invalids=", ".join(sorted(invalids))
            )
        )

    raise exception.SphinxConfError(
        'These conf.py attributes, "{invalids}" could not be found.'.format(
            invalids=", ".join(sorted(invalids))
        )
    )


def _print_fields(sphinx, fields=frozenset()):
    if not fields:
        attributes = _get_all_field_attributes(sphinx)
    elif len(fields) == 1:
        _, value = _get_field_attributes(sphinx, fields)[0]
        print(value)

        return
    else:
        attributes = _get_field_attributes(sphinx, fields)

    print("Found these conf.py values:")

    for name, value in sorted(attributes.items(), key=operator.itemgetter(0)):
        print("{name!s}:\n    {value!r}".format(name=name, value=value))


def print_fields_from_directory(directory, fields=frozenset()):
    package = finder.get_nearest_rez_package(directory)
    source_directory = doc_finder.get_source_from_package(package)
    sphinx = configuration.ConfPy.from_directory(source_directory)

    _print_fields(sphinx, fields=fields)
