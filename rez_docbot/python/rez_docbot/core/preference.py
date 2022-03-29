"""A module for describing all :ref:`rez_docbot` settings."""

import schema
from rez.config import config

from . import publisher_

_MASTER_KEY = "rez_docbot"
_PUBLISHERS = "publishers"

# TODO : Consider simplifying this schema
_MASTER_SCHEMA = schema.Schema(
    {_PUBLISHERS: [schema.Use(publisher_.Publisher.validate)]}
)


def get_base_settings(package=None):
    """Get the parsed classes for publishing documentation.

    Args:
        package (rez.packages.Package, optional):
            A package which may contain extra configuration overrides.
            Any override not found will be retrieved globally.

    Returns:
        dict[str, object]: The parsed user configuration settings.

    """
    # TODO : Need to add package override settings somewhere in here
    rez_user_options = config.optionvars  # pylint: disable=no-member

    data = rez_user_options.get(_MASTER_KEY) or dict()

    output = _MASTER_SCHEMA.validate(data)

    for publisher in output[_PUBLISHERS]:
        publisher.set_package(package)

    return output


def get_all_publishers(package):
    """Get every publish method registered globally and under ``package``.

    Important:
        The returned :class:`.Publisher` classes are not authenticated by
        default.  You need to call :meth:`.Publisher.authenticate` to connect
        them to a remote repository database (like `GitHub`_).

    Args:
        package (rez.packages.Package, optional):
            A package which may contain extra configuration overrides.
            Any override not found will be retrieved globally.

    Returns:
        list[Publisher]: Every registered publish method.

    """
    return get_base_settings(package=package)[_PUBLISHERS]


def get_first_versioned_view_url(package, allow_optionals=False):
    publishers = get_all_publishers(package)

    if not publishers:
        raise RuntimeError(
            'Global configuration + package "{package}" have no publishers.'.format(
                package=package
            )
        )

    optionals = []
    unversioned = []

    for publisher in publishers:
        if not publisher.is_required():
            optionals.append(publisher)

            if not allow_optionals:
                continue

        if not publisher.allow_versioned_publishes():
            continue

        return publisher.get_view_url()

    if unversioned:
        raise RuntimeError(
            'No required publisher "{unversioned}" supports versioning.'.format(
                unversioned=unversioned
            )
        )

    if optionals:
        raise RuntimeError(
            'No required publishers were found. Optional publishers '
            '"{optionals}" were ignored.'.format(
                optionals=optionals
            )
        )

    raise RuntimeError('Unknown error. Cannot continue.')
