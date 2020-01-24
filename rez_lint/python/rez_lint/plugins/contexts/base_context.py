#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""An abstract plugin module that sub-classes to compute data for other checker plugins to use."""

import abc

import six


@six.add_metaclass(abc.ABCMeta)
class BaseContext(object):
    """A plugin that is used to pre-compute information about Rez packages.

    These class instances run before checker plugin is run and the data
    can be queried by checker plugins later.

    """

    @staticmethod
    def get_order():
        """int: The priority of this plugin. To give higher priority, increase this value."""
        return 0

    @staticmethod
    @abc.abstractmethod
    def run(package, context):
        """Add context information to `context`, using data inside of `package`.

        Args:
            package (:class:`rez.packages_.DeveloperPackage`):
                The Rez package that will be queried to add information
                into `context`.
            context (:class:`.Context`):
                An object that will be modified by this method with
                new data. You're free to do whatever you want to this
                parameter - add, modify, or delete any data you'd like.

        """
        pass  # pragma: no cover
