#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Make sure :mod:`parso_helper.node_seek` works."""

import textwrap
import unittest

import parso
from parso_helper import node_seek


class GetNodeWithFirstPrefix(unittest.TestCase):
    """Make sure :func:`parso_helper.node_seek.get_node_with_first_prefix` works."""

    def test_current_node(self):
        """Get the given node assuming it defines its own prefix."""
        graph = parso.parse(
            textwrap.dedent(
                """\
                foo = [
                    blah,
                        another,
                ]
                """
            )
        )
        name_node = graph.get_first_leaf()
        self.assertEqual(
            name_node,
            node_seek.get_node_with_first_prefix(name_node),
        )

    def test_nested_prefix(self):
        """Get the prefix of a node whose prefix is stored in one of its child nodes."""
        graph = parso.parse(
            textwrap.dedent(
                """\
                foo = [
                    blah,
                        another,
                ]
                """
            )
        )
        name_node = graph.get_first_leaf()
        self.assertEqual(
            name_node,
            node_seek.get_node_with_first_prefix(graph),
        )


class IterNestedChildren(unittest.TestCase):
    """Make sure :func:`parso_helper.node_seek.iter_nested_children` works."""

    def test_empty(self):
        """Return no children because the node has no children."""
        graph = parso.parse("something = 8")
        name_node = graph.get_first_leaf()
        self.assertEqual([], list(node_seek.iter_nested_children(name_node)))

    def test_nested(self):
        """Return all children of a node."""
        graph = parso.parse("something = 8")
        self.assertEqual(
            [
                graph.children[0],
                graph.children[0].children[0],
                graph.children[0].children[1],
                graph.children[0].children[2],
                graph.children[1],
            ],
            list(node_seek.iter_nested_children(graph)),
        )


class IterParents(unittest.TestCase):
    """Make sure :func:`parso_helper.node_seek.iter_parents` works."""

    def test_empty(self):
        """Get no parents when a node has no parents."""
        graph = parso.parse("something = 8")
        self.assertEqual([], list(node_seek.iter_parents(graph)))

    def test_nested(self):
        """Get a every parent above a node."""
        graph = parso.parse("something = 8")
        expression_node = graph.get_first_leaf().parent
        self.assertEqual(
            [expression_node.parent],
            list(node_seek.iter_parents(expression_node)),
        )

    def test_single(self):
        """Get a single parent."""
        graph = parso.parse("something = 8")
        name_node = graph.get_first_leaf()
        self.assertEqual(
            [name_node.parent, name_node.parent.parent],
            list(node_seek.iter_parents(name_node)),
        )
