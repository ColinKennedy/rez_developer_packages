#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Generic functions that help iterating over containers and other iterables."""


def iter_is_last(container):
    count = len(container)

    for index, item in enumerate(container):
        if index + 1 < count:
            yield False, item
        else:
            yield True, item
