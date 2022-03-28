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
    """The parsed classes for publishing documentation.

    Args:
        package (rez.packages.Package, optional):
            A package which may contain extra configuration overrides.

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
    return get_base_settings(package=package)[_PUBLISHERS]
