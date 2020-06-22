#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json


# class BuiltinEncoder(json.JSONEncoder):
#     def default(self, object_):
#         if isinstance(object_, bool):
#             return str(object_)
#
#         if isinstance(object_, None):
#             return str(object_)
#
#         return super(BuiltinEncoder, self).default(object_)


class BuiltinEncoder(json.JSONEncoder):
    def default(self, obj):
        raise ValueError()
        if isinstance(obj, bool):
            return str(obj)

        if isinstance(obj, None):
            return str(obj)

        # Let the base class default method raise the TypeError
        return json.JSONEncoder.default(self, obj)

