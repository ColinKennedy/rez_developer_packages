#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Make sure that the plugin registry system of ``rez_lint`` works as expected."""

import os
import inspect
import sys
import tempfile
import textwrap

from python_compatibility.testing import common
from rez_lint.core import registry
from rez_lint import cli


class Registry(common.Common):
    """Make sure that the plugin registry system of ``rez_lint`` works as expected.

    Important:
        All modifications to :obj:`sys.path` and :obj:`os.environ` are
        auto-cleaned up by this class's base class.

    """

    @staticmethod
    def _initialize_all():
        registry.clear_checkers()
        registry.clear_contexts()
        cli._register_internal_plugins.has_run = False
        cli._register_internal_plugins()

    def setUp(self):
        super(Registry, self).setUp()

        self._initialize_all()  # Make doubly certain we're working with a clean slate

    def tearDown(self):
        super(Registry, self).setUp()

        self._initialize_all()

    def _make_basic_environment(self, text):
        current_plugins = len(registry.get_checkers() + registry.get_contexts())

        root = tempfile.mkdtemp(suffix="_some_python_path_root")
        self.add_item(root)
        sys.path.append(root)

        with open(os.path.join(root, "some_module.py"), "w") as handler:
            handler.write(text)

        _convert_to_importable_namespace(handler.name, root)
        namespace = _convert_to_importable_namespace(handler.name, root)

        os.environ["REZ_LINT_PLUGIN_PATHS"] = namespace
        cli._register_external_plugins()

        return current_plugins

    def test_do_nothing(self):
        """Don't register any new plugins."""
        current_plugins = self._make_basic_environment("")
        self.assertEqual(
            current_plugins, len(registry.get_checkers() + registry.get_contexts()),
        )

    def test_register_automatic(self):
        """Register a new context and checker plugin, using the subclassing method."""
        current_plugins = self._make_basic_environment(
            textwrap.dedent(
                """\
                from rez_lint.plugins.checkers import base_checker

                class Something(base_checker.BaseChecker):
                    def run(package, context):
                        return []
                """
            )
        )

        all_plugins = registry.get_checkers() + registry.get_contexts()
        self.assertEqual(current_plugins + 1, len(all_plugins))
        self.assertTrue("Something" in {plugin.__name__ for plugin in all_plugins})

    def test_register_manual(self):
        """Allow the user to manually register a custom class."""
        current_plugins = self._make_basic_environment(
            textwrap.dedent(
                """\
                from rez_lint.core import registry
                from rez_lint.plugins.checkers import base_checker

                class FakePlugin(object):
                    @staticmethod
                    def get_long_code():
                        return "foo-bar"

                    def get_order():
                        return 0

                    def run(package, context):
                        return []

                fake_plugin = FakePlugin()
                registry.register_checker(fake_plugin)
                """
            )
        )

        all_plugins = registry.get_checkers() + registry.get_contexts()
        self.assertEqual(current_plugins + 1, len(all_plugins))
        self.assertTrue("FakePlugin" in {plugin.__name__ if inspect.isclass(plugin) else plugin.__class__.__name__ for plugin in all_plugins})

    def test_already_registered(self):
        """Don't allow the user to register something that is already registered."""
        current_plugins = self._make_basic_environment(
            textwrap.dedent(
                """\
                from rez_lint.plugins.checkers import base_checker

                class Something(base_checker.BaseChecker):
                    def run(package, context):
                        return []
                """
            )
        )

        cli._register_external_plugins()


def _convert_to_importable_namespace(path, root):
    relative = os.path.relpath(path, root)
    no_extension = os.path.splitext(relative)[0]

    return os.path.normpath(no_extension).replace(os.sep, ".")
