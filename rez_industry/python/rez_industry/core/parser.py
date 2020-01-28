#!/usr/bin/env python
# -*- coding: utf-8 -*-

import parso

from . import parser_adapter

_ADAPTERS = {
    "help": parser_adapter.HelpAdapter,
    "tests": parser_adapter.TestsAdapter,
}


def add_to_attribute(attribute, data, code):
    try:
        adapter = _ADAPTERS[attribute]
    except KeyError:
        raise ValueError('Attribute "{attribute}" is not supported. Options were "{_ADAPTERS}".'
                         ''.format(attribute=attribute, _ADAPTERS=sorted(_ADAPTERS)))

    graph = parso.parse(code)

    return adapter.modify_with_existing(graph, data)
