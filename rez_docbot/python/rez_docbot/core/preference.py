"""A module for describing all :ref:`rez_docbot` settings."""

import schema

from rez.config import config

from . import publisher_


_MASTER_KEY = "rez_docbot"
# TODO : Consider simplifying this schema
_MASTER_SCHEMA = schema.Schema({"publishers": [schema.Use(publisher_.Publisher.validate)]})


def get_base_settings():
    """dict[str, object]: The parsed classes for publishing documentation."""
    rez_user_options = config.optionvars  # pylint: disable=no-member

    data = rez_user_options.get(_MASTER_KEY) or dict()

    return _MASTER_SCHEMA.validate(data)
