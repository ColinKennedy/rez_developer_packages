#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""All tests which don't belong to a specific category of import."""

import textwrap

from . import common


class DontChange(common.Common):
    """Make sure imports that shouldn't be changed aren't. But those that must change, do."""

    def test_import_001(self):
        """Replace only one flat namespace import."""
        code = textwrap.dedent(
            """\
            import something
            import foo
            """
        )

        namespaces = [("something", "another")]
        expected = textwrap.dedent(
            """\
            import another
            import foo
            """
        )

        self._test(expected, code, namespaces, partial=False)

    def test_import_002(self):
        """Replace only one nested namespace import."""
        code = textwrap.dedent(
            """\
            import something.parse
            import foo.parse
            """
        )

        namespaces = [("something", "another")]
        expected = textwrap.dedent(
            """\
            import another.parse
            import foo.parse
            """
        )

        self._test(expected, code, namespaces, partial=False)

    def test_from_import_001(self):
        """Replace a flat from-import."""
        code = textwrap.dedent(
            """\
            from foo import bar
            from thing import another
            """
        )

        namespaces = [("foo.bar", "bazz.something")]
        expected = textwrap.dedent(
            """\
            from bazz import something
            from thing import another
            """
        )

        self._test(expected, code, namespaces, partial=False)

    def test_from_import_002(self):
        """Replace a nested from-import."""
        code = textwrap.dedent(
            """\
            from foo.something import bar
            from thing.more import another
            """
        )

        namespaces = [("foo.something.bar", "bazz.something.else_here")]
        expected = textwrap.dedent(
            """\
            from bazz.something import else_here
            from thing.more import another
            """
        )

        self._test(expected, code, namespaces, partial=False)

    def test_mixed(self):
        """Replace some imports but not everything."""
        code = textwrap.dedent(
            """\
            from foo.something import bar
            import something.parse
            from thing.more import another
            import foo.parse
            """
        )

        namespaces = [
            ("foo.something.bar", "bazz.something.else_here"),
            ("something.parse", "another.parse"),
        ]

        expected = textwrap.dedent(
            """\
            from bazz.something import else_here
            import another.parse
            from thing.more import another
            import foo.parse
            """
        )

        self._test(expected, code, namespaces, partial=False)


class Backslashes(common.Common):
    r"""Check that imports-with-"\"s still replace as expected."""

    def test_001(self):
        """Replace imports with backslashes."""
        code = textwrap.dedent(
            """\
            import os.path, \\
                textwrap
            """
        )

        namespaces = [("textwrap", "another")]

        expected = textwrap.dedent(
            """\
            import os.path, \\
                another
            """
        )

        self._test(expected, code, namespaces, partial=False)

    def test_002(self):
        """Replace imports with backslashes."""
        code = textwrap.dedent(
            """\
            import os.path, \\
                    textwrap
            """
        )

        namespaces = [("os.path", "another")]

        expected = textwrap.dedent(
            """\
            import another, \\
                    textwrap
            """
        )

        self._test(expected, code, namespaces, partial=False)

    def test_003(self):
        """Replace imports with backslashes."""
        code = textwrap.dedent(
            """\
            import os.path, \\
                    textwrap, \\
                another
            """
        )

        namespaces = [("os.path", "something_else")]
        expected = textwrap.dedent(
            """\
            import something_else, \\
                    textwrap, \\
                another
            """
        )
        self._test(expected, code, namespaces, partial=False)
        self._test(expected, code, namespaces, partial=True)

        namespaces = [("textwrap", "blah")]
        expected = textwrap.dedent(
            """\
            import os.path, \\
                    blah, \\
                another
            """
        )
        self._test(expected, code, namespaces, partial=False)

        namespaces = [
            ("os.path", "blah"),
            ("textwrap", "blah"),
        ]
        expected = textwrap.dedent(
            """\
            import blah, \\
                    blah, \\
                another
            """
        )
        self._test(expected, code, namespaces, partial=False)

    def test_004(self):
        """Replace imports with backslashes."""
        code = textwrap.dedent(
            """\
            import os.path, \\
                    textwrap
            """
        )

        namespaces = [("os", "another")]

        expected = textwrap.dedent(
            """\
            import another.path, \\
                    textwrap
            """
        )

        self._test(expected, code, namespaces, partial=True)

    def test_005(self):
        """Replace multiple imports in the same `import X, Y, Z` statement."""
        code = textwrap.dedent(
            """\
            import os.path, \\
                    textwrap, \\
                os
            """
        )

        namespaces = [
            ("os.path", "something_else"),
            ("os", "something_else"),
        ]
        expected = textwrap.dedent(
            """\
            import something_else, \\
                    textwrap, \\
                something_else
            """
        )
        self._test(expected, code, namespaces, partial=True)

    def test_from_001(self):
        """Replace imports with backslashes."""
        code = textwrap.dedent(
            """\
            from thing import path, \\
                textwrap
            """
        )

        namespaces = [("thing", "blah")]
        expected = textwrap.dedent(
            """\
            from blah import path, \\
                textwrap
            """
        )
        self._test(expected, code, namespaces, partial=True)

        namespaces = [("thing.textwrap", "blah.another")]
        expected = textwrap.dedent(
            """\
            from blah import another
            from thing import path
            """
        )
        self._test(expected, code, namespaces, partial=True)

    def test_from_002(self):
        """Replace imports with backslashes."""
        code = textwrap.dedent(
            """\
            from blah import path, \\
                    textwrap
            """
        )

        namespaces = [
            ("blah.path", "another.thingy"),
            ("blah", "another"),
        ]
        expected = textwrap.dedent(
            """\
            from another import thingy
            from another import \\
                    textwrap
            """
        )
        self._test(expected, code, namespaces, partial=True)

        namespaces = [("blah.path", "another.thingy")]
        expected = textwrap.dedent(
            """\
            from another import thingy
            from blah import \\
                    textwrap
            """
        )
        self._test(expected, code, namespaces, partial=True)
        self._test(expected, code, namespaces, partial=False)

    def test_from_003(self):
        """Replace imports with backslashes."""
        code = textwrap.dedent(
            """\
            from mit import path, \\
                    textwrap, \\
                another
            """
        )

        namespaces = [("mit", "cornell")]
        expected = textwrap.dedent(
            """\
            from cornell import path, \\
                    textwrap, \\
                another
            """
        )
        self._test(expected, code, namespaces, partial=True)

        namespaces = [("mit.textwrap", "cornell.blah")]
        expected = textwrap.dedent(
            """\
            from cornell import blah
            from mit import path, \\
                another
            """
        )
        self._test(expected, code, namespaces, partial=True)

        namespaces = [
            ("mit.textwrap", "cornell.blah"),
            ("mit", "cornell"),
        ]

        expected = textwrap.dedent(
            """\
            from cornell import blah
            from cornell import path, \\
                another
            """
        )
        self._test(expected, code, namespaces, partial=True)


class Parentheses(common.Common):
    """Check that imports-with-()s still replace as expected."""

    def test_001(self):
        """Replace a single-namespace import that uses parentheses."""
        code = "from thing.something import (parse as blah)"
        namespaces = [("thing.something.parse", "another.jpeg.many.items")]
        expected = "from another.jpeg.many import (items as blah)"

        self._test(expected, code, namespaces)

    def test_002(self):
        """Replace a multi-namespace import that uses parentheses."""
        code = "from thing.something import (parse as blah, more_items)"

        namespaces = [("thing.something", "another.jpeg.many")]
        expected = "from another.jpeg.many import (parse as blah, more_items)"
        self._test(expected, code, namespaces, partial=True)

        namespaces = [
            ("thing.something.parse", "another.jpeg.many.items"),
            ("thing.something", "another.jpeg.many"),
        ]
        expected = textwrap.dedent(
            """\
            from another.jpeg.many import items as blah
            from another.jpeg.many import ( more_items)"""
        )
        self._test(expected, code, namespaces, partial=True)

    def test_003(self):
        """Replace a multi-namespace import that uses parentheses and whitespace."""
        code = textwrap.dedent(
            """\
            from thing.something import (
                parse as blah,
                    more_items)
            """
        )

        namespaces = [("thing.something", "another.jpeg.many")]
        expected = textwrap.dedent(
            """\
            from another.jpeg.many import (
                parse as blah,
                    more_items)
            """
        )
        self._test(expected, code, namespaces, partial=True)

        namespaces = [("thing.something.parse", "another.jpeg.many.thing")]
        expected = textwrap.dedent(
            """\
            from another.jpeg.many import thing as blah
            from thing.something import (
                    more_items)
            """
        )
        self._test(expected, code, namespaces, partial=True)

    def test_004(self):
        """Replace a multi-namespace import that uses parentheses and whitespace."""
        code = textwrap.dedent(
            """\
            from thing.something import (
                parse as blah,
                    more_items
            )
            """
        )

        namespaces = [("thing.something", "another.jpeg.many")]
        expected = textwrap.dedent(
            """\
            from another.jpeg.many import (
                parse as blah,
                    more_items
            )
            """
        )
        self._test(expected, code, namespaces, partial=True)

        namespaces = [("thing.something.parse", "another.jpeg.many.doom")]
        expected = textwrap.dedent(
            """\
            from another.jpeg.many import doom as blah
            from thing.something import (
                    more_items
            )
            """
        )
        self._test(expected, code, namespaces, partial=True)

        namespaces = [
            ("thing.something.parse", "another.jpeg.many.doom"),
            ("thing.something", "another.jpeg.many"),
        ]
        expected = textwrap.dedent(
            """\
            from another.jpeg.many import doom as blah
            from another.jpeg.many import (
                    more_items
            )
            """
        )
        self._test(expected, code, namespaces, partial=True)
