"""A full Publisher implementation for `GitHub`_ and `GitHub Enterprise`_."""

import functools

import schema as schema_

from ..adapters import adapter_registry
from . import generic

_NAME = "github"


class Github(generic.GitPublisher):
    """A full Publisher implementation for `GitHub`_ and `GitHub Enterprise`_."""

    @classmethod
    def _get_schema(cls):
        """dict[object, object]: The required / optional structure for this instance."""
        schema = super(Github, cls)._get_schema()
        schema[generic.AUTHENICATION] = schema_.Use(
            functools.partial(adapter_registry.validate, _NAME)
        )

        return schema

    @classmethod
    def get_name(cls):
        """str: The value used to refer to this class, as a :ref:`publisher type`."""
        return _NAME
