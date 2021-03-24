#!/usr/bin/env python
# -*- coding: utf-8 -*-


def get_inner_imports(namespaces, attributes, partial=False):
    def _in(namespace, options):
        return namespace in options

    def _starts_with(namespace, options):
        for option in options:
            if namespace.startswith(option):
                return True

        return False

    if partial:
        predicate = _starts_with
    else:
        predicate = _in

    output = set()

    for namespace in namespaces:
        for old, new in attributes:
            if predicate(namespace, old.get_all_full_namespaces()):
                output.add((tuple(namespace.split(".")), tuple(new.get_full_namespace().split("."))))

    return output
