#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""An abstract class which is subclassed to implement new ``rez_lint`` issue checks."""

import abc
import collections

import six

Code = collections.namedtuple("Code", "short_name long_name")


@six.add_metaclass(abc.ABCMeta)
class BaseChecker(object):
    """Check for an issue in or around the user's Rez package."""

    @staticmethod
    @abc.abstractmethod
    def get_long_code():
        """str: The string used to refer to this class or disable it."""
        return ""  # pragma: no cover

    @staticmethod
    def get_order():
        """int: The execution order of this plugin. Increase this value to make it run sooner."""
        return 0

    @staticmethod
    @abc.abstractmethod
    def run(package, context):
        """Check the package for issues.

        Args:
            package (:class:`rez.packages_.DeveloperPackage`):
                The Rez package whose root directory will be used to
                search for a README file.
            context (:class:`.Context`):
                A data instance that keeps track of the user's input and
                any pre-computed data. This parameter exists to help
                share data across checker plugins.

        Returns:
            list[:class:`.Description`]:
                If no issues are found, return an empty list. Otherwise,
                return one description of each found issue.

        """
        return []  # pragma: no cover
