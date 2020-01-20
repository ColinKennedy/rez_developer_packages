#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Test classes and functions in the :mod:`rez_lint.plugins.contexts.packaging` module."""

import unittest


class SourceResolved(unittest.TestCase):
    """Test cases for the :class:`rez_lint.plugins.contexts.SourceResolvedContext` class."""

    def test_get_context(self):
        """Check that Rez can resolve a context correctly and return it."""
        raise NotImplementedError()

    def test_no_commands(self):
        """If the Rez package has no commands, make sure this does not cause an error.

        Instead, just have the context return early.

        """
        raise NotImplementedError()
