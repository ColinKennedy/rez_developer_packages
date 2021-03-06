#!/usr/bin/env python
# -*- coding: utf-8 -*-

import operator


def to_dot_namespace(names):
    return ".".join(map(operator.attrgetter("value"), names))
