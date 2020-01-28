#!/usr/bin/env python
# -*- coding: utf-8 -*-

import parso

from . import parser_adapter

_ADAPTERS = {
    "help": parser_adapter.HelpAdapter,
    "tests": parser_adapter.TestsAdapter,
}


def add_to_attribute(attribute, data, code):
    if not data:
        raise ValueError('Object "{data}" cannot be empty.'.format(data=data))

    try:
        adapter_class = _ADAPTERS[attribute]
    except KeyError:
        raise ValueError('Attribute "{attribute}" is not supported. Options were "{_ADAPTERS}".'
                         ''.format(attribute=attribute, _ADAPTERS=sorted(_ADAPTERS)))

    reason_why_invalid = adapter_class.check_if_invalid(data)

    if reason_why_invalid:
        raise ValueError('Data "{data}" is invalid. Reason "{reason_why_invalid}".'.format(data=data, reason_why_invalid=reason_why_invalid))

    graph = parso.parse(code)

    return adapter_class.modify_with_existing(graph, data)
