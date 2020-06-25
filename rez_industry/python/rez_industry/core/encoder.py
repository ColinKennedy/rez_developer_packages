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
            if item in ("null", '"null"'):
                results[  # pylint: disable=unsupported-assignment-operation
                    index
                ] = "None"
            if item == "false":
                results[  # pylint: disable=unsupported-assignment-operation
                    index
                ] = "False"
            if item == "true":
                results[  # pylint: disable=unsupported-assignment-operation
                    index
                ] = "True"

        return results
