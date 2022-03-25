"""Implement the :ref:`rez_sphinx build inspect-conf` command."""

import logging
import operator

from rez_utilities import finder

from ...core import configuration, doc_finder, exception

_LOGGER = logging.getLogger(__name__)


def _get_all_field_attributes(sphinx):
    """Get every attribute and value from ``sphinx``.

    Args:
        sphinx (configuration.ConfPy):
            The `conf.py`_ to query from for attributes.

    Returns:
        dict[str: object]: Each attribute name and its value.

    """
    attributes = sphinx.get_module_attributes()

    if attributes:
        return attributes

    path = sphinx.get_module_path()

    raise exception.SphinxConfError(
        'Configuration "{path}" has no found attributes.'.format(path=path)
    )


def _get_field_attributes(sphinx, fields):
    """Get every listed attribute name in ``fields`` from ``sphinx``.

    Args:
        sphinx (configuration.ConfPy):
            The `conf.py`_ to query from for attributes.
        fields (iter[str]):
            Each attribute name to return from ``sphinx``. All other attributes
            from ``sphinx`` are ignored.

    Raises:
        SphinxConfError:
            If any attribute name from ``fields`` could not be found in ``sphinx``.

    Returns:
        list[tuple[str, object]]: Each attribute name and its value.

    """
    attributes = {name: value for name, value in sphinx.get_module_attributes().items()}
    _LOGGER.debug(
        'Found conf.py attributes, "%s". From file, "%s"',
        ", ".join(sorted(attributes.keys())),
        sphinx.get_module_path(),
    )

    invalids = set()
    output = []
    count = 0

    for name in fields:
        count += 1

        if name not in attributes:
            invalids.add(name)
        else:
            output.append((name, attributes[name]))

    if not invalids:
        return output

    if count == 1:
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
    """Print all attribute names in ``fields``, using ``sphinx``.

    Args:
        sphinx (configuration.ConfPy):
            The `conf.py`_ to query from for attributes.
        fields (iter[str]):
            Each attribute name to return from ``sphinx``. All other attributes
            from ``sphinx`` are ignored.

    """
    if not fields:
        attributes = list(_get_all_field_attributes(sphinx).items())
    elif len(fields) == 1:
        _, value = _get_field_attributes(sphinx, fields)[0]
        print(value)

        return
    else:
        attributes = _get_field_attributes(sphinx, fields)

    print("Found these conf.py values:")

    for name, value in sorted(attributes, key=operator.itemgetter(0)):
        print("{name!s}:\n    {value!r}".format(name=name, value=value))


def print_fields_from_directory(directory, fields=frozenset()):
    """Print every `Sphinx`_ attribute in ``fields``.

    Args:
        directory (str):
            The absolute folder on-disk to where a Rez package + `conf.py`_ is expected.

    Raises:
        SphinxConfError: If `conf.py`_ was not found or unreadable.

    """
    package = finder.get_nearest_rez_package(directory)

    if package:
        source_directory = doc_finder.get_source_from_package(package)
    else:
        source_directory = directory

    if not configuration.ConfPy.is_valid_directory(source_directory):
        raise exception.SphinxConfError(
            'Directory "{source_directory}" has no conf.py file.'.format(
                source_directory=source_directory
            )
        )

    sphinx = configuration.ConfPy.from_directory(source_directory)
    _print_fields(sphinx, fields=fields)
