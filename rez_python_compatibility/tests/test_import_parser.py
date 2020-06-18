#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Test that import namespaces are found correctly."""

import sys
import textwrap

from python_compatibility import import_parser
from python_compatibility.testing import common, package_tester


class _TestCase(common.Common):
    """A common class for testing the "Python import parser"."""

    @staticmethod
    def _test_with_code(code):
        """Find Python import namespaces directly from Python source code.

        This function assumes that `code` does not contain any relative imports.

        Args:
            code (str): Python code that may or may not have Python imports.

        Returns:
            list[str]: The found Python namespaces.

        """
        return [
            module.get_namespace()
            for module in import_parser.parse_python_source_code(code)
        ]

    def _test_with_file(self, code):
        """Find Python import namespaces directly from Python source code.

        This method creates a test Python project.

        Args:
            code (str): Python code that may or may not have Python imports.

        Returns:
            list[str]: The found Python namespaces.

        """
        root, path = package_tester.make_fake_python_project()
        self.delete_item_later(root)
        sys.path.append(root)

        with open(path, "w") as handler:
            handler.write(code)

        return [
            module.get_namespace()
            for module in import_parser.get_namespaces_from_file(path)
        ]


class Complex(_TestCase):
    """Test more situational Python imports."""

    def test_nested(self):
        """Check nested for-loop."""
        code = textwrap.dedent(
            """\
            def function():
                def wrapper():
                    from foo import blah
            """
        )
        self.assertEqual(["foo.blah"], self._test_with_code(code))

    def test_very_complex(self):
        """Check that the most nested, conditional case for imports still works."""
        code = textwrap.dedent(
            """\
            class Class(object):
                def function(self):
                    def wrapper():
                        class Another(object):
                            for _ in range(2):
                                if True:
                                    try:
                                        from foo import blah
                                    except:
                                        pass
            """
        )
        self.assertEqual(["foo.blah"], self._test_with_code(code))

    def test_star(self):
        """Check that Python-star-style imports works."""
        code = "from foo.bar import *"
        self.assertEqual(["foo.bar"], self._test_with_code(code))


class Absolute(_TestCase):
    """Parse different styles of absolute Python imports."""

    def test_import_from(self):
        """Check `from foo import bar`."""
        code = "from foo import blah"
        self.assertEqual(["foo.blah"], self._test_with_code(code))

    def test_import_001(self):
        """Check `import X.Y`."""
        code = "import foo.blah"
        self.assertEqual(["foo.blah"], self._test_with_code(code))

    def test_import_002(self):
        """Check `import X`."""
        code = "import foo"
        self.assertEqual(["foo"], self._test_with_code(code))

    def test_multiple_items(self):
        """Check `import X, Y, Z`."""
        code = "import foo, bar, another.thing"
        results = self._test_with_code(code)
        self.assertEqual(3, len(results))
        self.assertEqual({"foo", "bar", "another.thing"}, set(results))


class Aliases(_TestCase):
    """Test every type of "Python absolute imports with aliases" gets the correct namespace."""

    def test_import_001(self):
        """Alias a dotted import."""
        code = "import chilly.night as thing"
        self.assertEqual(["chilly.night"], self._test_with_code(code))

    def test_import_002(self):
        """Alias a regular, absolute import."""
        code = "import hot as thing"
        self.assertEqual(["hot"], self._test_with_code(code))

    def test_import_from_001(self):
        """Alias a dotted from X import Y statement."""
        code = "from registry.chilly import night as thing"
        self.assertEqual(["registry.chilly.night"], self._test_with_code(code))

    def test_import_from_002(self):
        """Alias a from X import Y statement."""
        code = "from registry import hot as thing"
        self.assertEqual(["registry.hot"], self._test_with_code(code))

    def test_import_multiple_items(self):
        """Alias an import with multiple imports on the same line."""
        code = "import hot as thing, blah.whatever as something_else, stuff, os"
        results = self._test_with_code(code)
        self.assertEqual(4, len(results))
        self.assertEqual({"hot", "blah.whatever", "os", "stuff"}, set(results))

    def test_import_from_multiple_items(self):
        """Alias a from-import with multiple imports on the same line."""
        code = "from base.modules import item as thing, facebook as myspace, harry as potter"
        results = self._test_with_code(code)
        self.assertEqual(3, len(results))
        self.assertEqual(
            {"base.modules.facebook", "base.modules.harry", "base.modules.item"},
            set(results),
        )

    def test_import_multiple_items_mixed(self):
        """Alias a dotted import with multiple imports on the same line."""
        code = "import base.edge.item as thing, facebook as myspace, harry as potter"
        results = self._test_with_code(code)
        self.assertEqual(3, len(results))
        self.assertEqual({"base.edge.item", "facebook", "harry"}, set(results))


class RelativeAliases(_TestCase):
    """Test every type of "Python relative imports with aliases" gets the correct namespace."""

    def test_import_001(self):
        """Test a from-import with an alias."""
        code = "from . import hot as thing"
        self.assertEqual(["fake_package.inner_package.hot"], self._test_with_file(code))

    def test_import_from_001(self):
        """Test for a dotted relative path + alias."""
        code = "from .registry.chilly import night as thing"
        self.assertEqual(
            ["fake_package.inner_package.registry.chilly.night"],
            self._test_with_file(code),
        )

    def test_import_multiple_items(self):
        """Test a from-import with multiple with multiple aliases."""
        code = "from . import hot as thing, whatever as something_else, stuff, os"
        results = self._test_with_file(code)
        self.assertEqual(4, len(results))
        self.assertEqual(
            {
                "fake_package.inner_package.hot",
                "fake_package.inner_package.os",
                "fake_package.inner_package.stuff",
                "fake_package.inner_package.whatever",
            },
            set(results),
        )

    def test_import_from_multiple_items(self):
        """Test a from-import with parent modules with multiple aliases."""
        code = "from .base.modules import item as thing, facebook as myspace, harry as potter"
        results = self._test_with_file(code)
        self.assertEqual(3, len(results))
        self.assertEqual(
            {
                "fake_package.inner_package.base.modules.facebook",
                "fake_package.inner_package.base.modules.harry",
                "fake_package.inner_package.base.modules.item",
            },
            set(results),
        )

    def test_import_multiple_items_mixed(self):
        """Test a from-import with parent modules with multiple aliases."""
        code = "from ..base.edge import item as thing, facebook as myspace, harry as potter"
        results = self._test_with_file(code)
        self.assertEqual(3, len(results))
        self.assertEqual(
            {
                "fake_package.base.edge.facebook",
                "fake_package.base.edge.harry",
                "fake_package.base.edge.item",
            },
            set(results),
        )
