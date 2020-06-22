#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json


class BuiltinEncoder(json.JSONEncoder):
    def iterencode(self, o, _one_shot=False):
        results = super(BuiltinEncoder, self).iterencode(o, _one_shot=_one_shot)

        for index, item in enumerate(results):
            if item in ("null", '"null"'):
                results[index] = "None"
            if item == "false":
                results[index] = "False"
            if item == "true":
                results[index] = "True"

        return results
