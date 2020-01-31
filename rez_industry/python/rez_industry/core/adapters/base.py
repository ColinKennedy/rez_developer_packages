#!/usr/bin/env python
# -*- coding: utf-8 -*-

import abc

import six


@six.add_metaclass(abc.ABCMeta)
class BaseAdapter(object):
    """A class that is used to modify a Rez package definition."""

    @staticmethod
    def supports_duplicates():
        return False

    @staticmethod
    @abc.abstractmethod
    def check_if_invalid(data):
        """str: If `data` is invalid, return a message explaining why."""
        return ""

    @staticmethod
    @abc.abstractmethod
    def modify_with_existing(graph, data):
        pass
