#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The main class used to modify a user's Rez package.py file."""

import abc

import six


@six.add_metaclass(abc.ABCMeta)
class BaseAdapter(object):
    """A class that is used to modify a Rez package definition."""

    @staticmethod
    def supports_duplicates():
        """bool: Enable "append" support for this class, if set to True."""
        return False

    @staticmethod
    @abc.abstractmethod
    def check_if_invalid(data):  # pragma: no cover
        """str: If `data` is invalid, return a message explaining why."""
        return ""

    @staticmethod
    @abc.abstractmethod
    def modify_with_existing(graph, data):  # pragma: no cover
        """Add `data` to a parso node `graph`.

        Args:
            graph (:class:`parso.python.Tree.PythonBaseNode`):
                Some node that will either be appended to or have some
                of its contents overwritten and returned.
            data (object):
                Whatever data will be added to `graph`. It's up to
                subclasses to figure out what kind of data is needed and
                how it will be added.

        Returns:
            str:
                The modified Python source code. It should resemble the
                source code of `graph` plus any serialized `data`.

        """
        pass
