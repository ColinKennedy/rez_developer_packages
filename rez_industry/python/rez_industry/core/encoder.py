#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""A fake JSON Encoder class so we can intercept javascript code before it causes problems."""

import json


class BuiltinEncoder(json.JSONEncoder):
    """A fake JSON Encoder class so we can intercept javascript code before it causes problems."""

    def iterencode(self, o, _one_shot=False):
        """Replace boolean and null values with "Python-safe" alternatives."""
        results = super(BuiltinEncoder, self).iterencode(o, _one_shot=_one_shot)

        for index, item in enumerate(results):
            new = item
            new = new.replace('"null"', '"None"')
            new = new.replace("null", "None")
            new = new.replace("false", "False")
            new = new.replace("true", "True")

            if new != item:
                results[  # pylint: disable=unsupported-assignment-operation
                    index
                ] = new

        return results
