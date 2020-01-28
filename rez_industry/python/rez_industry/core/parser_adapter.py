#!/usr/bin/env python
# -*- coding: utf-8 -*-

import abc

from rez import package_serialise
from rez.vendor.schema import schema

import six


@six.add_metaclass(abc.ABCMeta)
class BaseAdapter(object):
    @staticmethod
    @abc.abstractmethod
    def check_if_invalid(data):
        return ""

    @staticmethod
    @abc.abstractmethod
    def modify_with_existing(graph, data):
        pass


class HelpAdapter(BaseAdapter):
    @staticmethod
    def check_if_invalid(data):
        try:
            package_serialise.package_serialise_schema.validate({
                "name": "",  # This key is required so we just give it nothing
                "help": data,
            })
        except schema.SchemaError as error:
            return str(error)

        return ""

    @staticmethod
    def modify_with_existing(graph, data):
        raise NotImplementedError()


class TestsAdapter(BaseAdapter):
    @staticmethod
    def check_if_invalid(data):
        try:
            package_serialise.package_serialise_schema.validate({
                "name": "",  # This key is required so we just give it nothing
                "tests": data,
            })
        except schema.SchemaError as error:
            return str(error)

        return ""

    @staticmethod
    def modify_with_existing(graph, data):
        raise ValueError(data)
        raise NotImplementedError()
