#!/usr/bin/env python
# -*- coding: utf-8 -*-


from rez import package_serialise
from rez.vendor.schema import schema

from . import base


class HelpAdapter(base.BaseAdapter):
    @staticmethod
    def supports_duplicates():
        return True

    @staticmethod
    def check_if_invalid(data):
        """str: If `data` is not a str or list-of-lists, return a message."""
        try:
            package_serialise.package_serialise_schema.validate(
                {
                    "name": "",  # This key is required so we just give it nothing
                    "help": data,
                }
            )
        except schema.SchemaError as error:
            return str(error)

        return ""

    @staticmethod
    def modify_with_existing(graph, data, append=False):
        raise NotImplementedError()
