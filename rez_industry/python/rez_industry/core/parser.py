#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import parso

from rez import packages_

from . import parser_adapter

_ADAPTERS = {
    "help": parser_adapter.HelpAdapter,
    "tests": parser_adapter.TestsAdapter,
}


def add_to_attribute(attribute, data, path):
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

    with open(path, "r") as handler:
        code = handler.read()

    graph = parso.parse(code)

    # TODO : Consider changing this in the future. We shouldn't need to
    # read the package.py just to get existing value. We should just
    # parse the existing values out, using `parso`.
    #
    package = packages_.get_developer_package(os.path.dirname(path))

    return adapter_class.modify_with_existing(graph, data, package)
