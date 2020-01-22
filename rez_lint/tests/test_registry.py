#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Make sure that the plugin registry system of ``rez_lint`` works as expected."""

import inspect
import os
import sys
import tempfile
import textwrap

from python_compatibility.testing import common
from rez_lint import cli
from rez_lint.core import registry


class Registry(common.Common):
    """Make sure that the plugin registry system of ``rez_lint`` works as expected.

    Important:
        All modifications to :obj:`sys.path` and :obj:`os.environ` are
        auto-cleaned up by this class's base class.

    """

    @staticmethod
    def _initialize_all():
        """Delete all registered classes."""
        registry.clear_checkers()
        registry.clear_contexts()
        cli._register_internal_plugins.has_run = (
            False  # pylint: disable=protected-access
        )
        cli._register_internal_plugins()  # pylint: disable=protected-access

    def setUp(self):
        """Delete all registered classes."""
        super(Registry, self).setUp()

        self._initialize_all()  # Make doubly certain we're working with a clean slate

    def tearDown(self):
        """Delete all registered classes."""
        super(Registry, self).tearDown()

        self._initialize_all()

    def _make_basic_environment(self, text):
        """Make a Python plugin file and make it importable - and then get its plugins.

        Args:
            text (str): The Python source code that will be used to register new plugins.

        """
        current_plugins = len(registry.get_checkers() + registry.get_contexts())

        root = tempfile.mkdtemp(suffix="_some_python_path_root")
        self.add_item(root)
        sys.path.append(root)

        with tempfile.NamedTemporaryFile(suffix=".py", delete=True) as handler:
            pass

        with open(os.path.join(root, os.path.basename(handler.name)), "w") as handler:
            handler.write(text)

        _convert_to_importable_namespace(handler.name, root)
        namespace = _convert_to_importable_namespace(handler.name, root)

        os.environ["REZ_LINT_PLUGIN_PATHS"] = namespace
        cli._register_external_plugins.has_run = (
            False  # pylint: disable=protected-access
        )
        cli._register_external_plugins()  # pylint: disable=protected-access

        return current_plugins

    def test_register_automatic(self):
        """Register a new context and checker plugin, using the subclassing method."""
        all_plugins = registry.get_checkers() + registry.get_contexts()
        self.assertFalse("Something" in {plugin.__name__ for plugin in all_plugins})

        self._make_basic_environment(
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
        self.assertTrue("Something" in {plugin.__name__ for plugin in all_plugins})

    def test_register_manual(self):
        """Allow the user to manually register a custom class."""
        all_plugins = registry.get_checkers() + registry.get_contexts()
        self.assertFalse("FakePlugin" in {plugin.__name__ for plugin in all_plugins})

        self._make_basic_environment(
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

        self.assertTrue(
            "FakePlugin"
            in {
                plugin.__name__
                if inspect.isclass(plugin)
                else plugin.__class__.__name__
                for plugin in all_plugins
            }
        )

    def test_already_registered_001(self):
        """Allow the user to accidentally register the same plugins twice.

        We do this because it may happen by accident. Plus, they aren't
        explicitly registering the plugin. So it feels safe to allow.

        """
        self._make_basic_environment(
            textwrap.dedent(
                """\
                from rez_lint.plugins.checkers import base_checker

                class Something(base_checker.BaseChecker):
                    def run(package, context):
                        return []
                """
            )
        )

        cli._register_external_plugins.has_run = (
            False  # pylint: disable=protected-access
        )
        cli._register_external_plugins()  # pylint: disable=protected-access

    def test_already_registered_002(self):
        """Don't allow the user to explicitly register the same plugin more than once."""

        class MyChecker(object):
            """Do nothing."""

            @staticmethod
            def get_long_code():
                """Do nothing."""
                return "something"

            @staticmethod
            def get_order():
                """Do nothing."""
                return 0

            @staticmethod
            def run(_, __):
                """Do nothing."""
                return []

        class MyContext(object):
            """Do nothing."""

            @staticmethod
            def get_order():
                """Do nothing."""
                return 0

            @staticmethod
            def run(_, __):
                """Do nothing."""
                return

        registry.register_checker(MyChecker)

        with self.assertRaises(EnvironmentError):
            registry.register_checker(MyChecker)

        registry.register_context(MyContext)

        with self.assertRaises(EnvironmentError):
            registry.register_context(MyContext)


def _convert_to_importable_namespace(path, root):
    relative = os.path.relpath(path, root)
    no_extension = os.path.splitext(relative)[0]

    return os.path.normpath(no_extension).replace(os.sep, ".")
