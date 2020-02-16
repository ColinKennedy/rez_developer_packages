#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Check that setting / replacing imports works as expected."""

import tempfile
import textwrap

from move_break import cli
from python_compatibility.testing import common


class _Common(common.Common):
    """A base clsas used by other test classes."""

    def _test(  # pylint: disable=too-many-arguments
        self, expected, code, namespaces, partial=False, aliases=False
    ):
        """Make a temporary file to test with and delete it later.

        Args:
            expected (str):
                The modified code, with whatever namespaces changes were
                requested.
            code (str):
                The text of a Python file that (presumably) has imports
                that we must replace.
            namespaces (list[tuple[str, str]]):
                A pair of Python dot-separated import namespaces. It's
                an existing namespace + whatever namespace that will
                replace it.
            partial (bool, optional):
                If True, allow namespace replacement even if the user
                doesn't provide 100% of the namespace. If False, they must
                describe the entire import namespace before it can be
                renamed. Default is False.
            aliases (bool, optional):
                If True and replacing a namespace would cause Python
                statements to fail, auto-add an import alias to ensure
                backwards compatibility If False, don't add aliases. Default
                is False.

        """
        with tempfile.NamedTemporaryFile(suffix=".py", delete=False) as handler:
            handler.write(code)

        self.delete_item_later(handler.name)

        cli.move_imports({handler.name}, namespaces, partial=partial, aliases=aliases)

        with open(handler.name, "r") as handler:
            new_code = handler.read()

        self.assertEqual(expected, new_code)


class Inputs(_Common):
    """Check that different text input behaves in predictable ways."""

    def test_empty(self):
        """Don't let someone input an import list of namespaces."""
        code = "import something"
        namespaces = []
        expected = "import something"

        with self.assertRaises(ValueError):
            self._test(expected, code, namespaces, partial=True)

    def test_invalid(self):
        """If namespaces isn't a list of pairs, raise an exception."""
        code = "import something"
        namespaces = None
        expected = "import something"

        with self.assertRaises(ValueError):
            self._test(expected, code, namespaces, partial=True)

        namespaces = ['something']

        with self.assertRaises(ValueError):
            self._test(expected, code, namespaces, partial=True)


# class Aliases(_Common):
#     """Add aliases to import statements."""
#
#     def test_from_001(self):
#         """Add an alias to a "nested" from-import."""
#         code = "from foo.bar import thing"
#         namespaces = [("foo.bar.thing", "something.parse.blah")]
#         expected = "from something.parse import blah as thing"
#
#         self._test(expected, code, namespaces, partial=True, aliases=True)
#
#     def test_from_002(self):
#         """Add an alias to a "flat" from-import."""
#         code = "from foo import thing"
#         namespaces = [("foo.thing", "something.parse")]
#         expected = "from something import parse as thing"
#
#         self._test(expected, code, namespaces, partial=True, aliases=True)
#
#     def test_from_003(self):
#         """Add an alias to a split from-import."""
#         code = "from foo.thing import another, one"
#         namespaces = [("foo.thing.another", "something.parse")]
#         expected = textwrap.dedent(
#             """\
#             from something import parse as another
#             from foo.thing import one
#             """
#         )
#
#         self._test(expected, code, namespaces, partial=True, aliases=True)


class DontChange(_Common):
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


class Imports(_Common):
    """A class to check if import replacement works correctly."""

    def test_empty_001(self):
        """Allow an empty Python module as input (even though it does nothing)."""
        code = ""
        namespaces = [("something", "another")]
        expected = ""

        self._test(expected, code, namespaces)

    def test_empty_002(self):
        """Require the user to always pass non-empty namespaces."""
        code = ""
        namespaces = []
        expected = ""

        with self.assertRaises(ValueError):
            self._test(expected, code, namespaces)

    def test_same_namespaces(self):
        """If any old and new namespace pair is the same, then raise an exception."""
        code = ""
        namespaces = [("something.foo", "something.foo")]
        expected = ""

        with self.assertRaises(ValueError):
            self._test(expected, code, namespaces)

    def test_normal_001(self):
        """Replace a basic, minimum import."""
        code = "import something"
        namespaces = [("something", "another")]
        expected = "import another"

        self._test(expected, code, namespaces, partial=True)

    def test_normal_002(self):
        """Replace a nested namespace import."""
        code = "import something.parse"
        namespaces = [("something", "another")]
        expected = "import another.parse"

        self._test(expected, code, namespaces, partial=True)

    def test_normal_003(self):
        """Partially replace a nested namespace import."""
        code = "import something.parse"
        namespaces = [("something", "another")]
        expected = "import another.parse"

        self._test(expected, code, namespaces, partial=True)

    def test_normal_004(self):
        """Relace a nested namespace import with an import that isn't nested."""
        code = "import something.parse"
        namespaces = [("something.parse", "another")]
        expected = "import another"

        self._test(expected, code, namespaces, partial=True)

    def test_normal_005(self):
        """Replace a nested namespace import with an even more nested one."""
        code = "import something.parse"
        namespaces = [("something.parse", "another.with.many.items")]
        expected = "import another.with.many.items"

        self._test(expected, code, namespaces, partial=True)

    def test_normal_006(self):
        """Replace an import that has an alias - and keep the original alias."""
        code = "import something.parse as blah"
        namespaces = [("something.parse", "another.with.many.items")]
        expected = "import another.with.many.items as blah"

        self._test(expected, code, namespaces, partial=True)

    def test_parentheses_import_001(self):
        """Replace a single-namespace import that uses parentheses."""
        code = "from thing.something import (parse as blah)"
        namespaces = [("thing.something.parse", "another.jpeg.many.items")]
        expected = "from another.jpeg.many import (items as blah)"

        self._test(expected, code, namespaces, partial=True)

    def test_parentheses_import_002(self):
        """Replace a multi-namespace import that uses parentheses."""
        code = "from thing.something import (parse as blah, more_items)"
        namespaces = [("thing.something.parse", "another.jpeg.many.items")]
        expected = "from another.jpeg.many import (items as blah, more_items)"

        self._test(expected, code, namespaces, partial=True)

    def test_parentheses_import_003(self):
        """Replace a multi-namespace import that uses parentheses and whitespace."""
        code = textwrap.dedent(
            """\
            from thing.something import (
                parse as blah,
                    more_items)
            """
        )
        namespaces = [("thing.something.parse", "another.jpeg.many.items")]
        expected = textwrap.dedent(
            """\
            from another.jpeg.many import (
                items as blah,
                    more_items)
            """
        )

        self._test(expected, code, namespaces, partial=True)

    def test_parentheses_import_004(self):
        """Replace a multi-namespace import that uses parentheses and whitespace."""
        code = textwrap.dedent(
            """\
            from thing.something import (
                parse as blah,
                    more_items
            )
            """
        )
        namespaces = [("thing.something.parse", "another.jpeg.many.items")]
        expected = textwrap.dedent(
            """\
            from another.jpeg.many import (
                items as blah,
                    more_items
            )
            """
        )

        self._test(expected, code, namespaces, partial=True)

    def test_commas(self):
        """Replace multiple imports at once."""
        code = "import something, lots.of.items, another, os.path, textwrap"
        namespaces = [
            ("another", "new_location.more.parts.here"),  # extra dots replacement
            ("os", "new_os"),  # beginning replacement
            ("lots.of.items", "foo"),  # less dots replacement
            ("textwrap", "os"),  # full replacement
        ]
        expected = (
            "import something, foo, new_location.more.parts.here, new_os.path, os"
        )

        self._test(expected, code, namespaces, partial=True)

    def test_complex(self):
        """Replace imports even in a more complicated scenario."""
        code = textwrap.dedent(
            """\
            import thing.bar.more.items as thing
            import something_else.more.items
            """
        )

        namespaces = [
            ("thing.bar", "different_location.here"),
            ("something_else.more.items", "foo"),
        ]

        expected = textwrap.dedent(
            """\
            import different_location.here.more.items as thing
            import foo
            """
        )

        self._test(expected, code, namespaces, partial=True)

    def test_from_001(self):
        """Replace a from import with a different nested namespace."""
        code = "from foo.bar import thing"
        namespaces = [("foo.bar", "something.parse")]
        expected = "from something.parse import thing"

        self._test(expected, code, namespaces, partial=True)

    def test_from_002(self):
        """Target and replace a contiguous `foo.bar` across a split `from foo import bar`."""
        code = "from foo import bar"
        namespaces = [("foo.bar", "something.parse")]
        expected = "from something import parse"

        self._test(expected, code, namespaces, partial=True)

    def test_from_003(self):
        """Reduce the base namespace but only partially."""
        code = "from foo.bar.thing import another"
        namespaces = [("foo.bar", "blah")]
        expected = "from blah.thing import another"

        self._test(expected, code, namespaces, partial=True)

    def test_from_004(self):
        """Split a from import where part of the namespace is in the imported names."""
        code = "from foo import another"
        namespaces = [("foo.another", "blah.block.items")]
        expected = "from blah.block import items"

        self._test(expected, code, namespaces, partial=True)

    def test_from_005(self):
        """Reduce the base namespace completely."""
        code = "from foo.block.items import another"
        namespaces = [("foo.block.items", "items")]
        expected = "from items import another"

        self._test(expected, code, namespaces, partial=True)

    def test_from_comma_no_replace(self):
        """Don't replace a from import completely because some namespaces are missing."""
        code = "from foo import bar, another"
        namespaces = [
            ("foo.bar", "something.parse"),
        ]
        expected = textwrap.dedent(
            """\
            from something import parse
            from foo import another"""
        )

        self._test(expected, code, namespaces, partial=False)

    def test_from_comma_replace(self):
        """Fully replace one namespace with another."""
        code = "from foo import bar, another"
        namespaces = [
            ("foo.bar", "something.parse"),
            ("foo.another", "something.another"),
        ]
        expected = "from something import parse, another"

        self._test(expected, code, namespaces, partial=True)

    # def test_from_complex(self):
    #     """Check that complicated whitespace still replaces imports correctly."""
    #     code = textwrap.dedent(
    #         """\
    #         from something.parso import (
    #             blah as whatever, bazz,
    #             etc as more,
    #                     another_line as thing,
    #                 bad_formatting,
    #         )
    #         """
    #     )
    #
    #     namespaces = [
    #         ("something.parso.blah", "a_new.namespace_here"),
    #         ("something.parso.etc", "etc.dedicated.namespace"),
    #     ]
    #
    #     expected = textwrap.dedent(
    #         """\
    #         from a_new import namespace_here as whatever
    #         from etc.dedicated import namespace as more
    #         from something.parso import (
    #             bazz,
    #                     another_line as thing,
    #                 bad_formatting,
    #         )
    #         """
    #     )
    #
    #     self._test(expected, code, namespaces, partial=False)

    # def test_from_complex(self):
    #     """Check that complicated whitespace still replaces imports correctly."""
    #     code = textwrap.dedent(
    #         """\
    #         from something.parse import (
    #             bazz,
    #             etc as more,
    #             another_line as thing,
    #                 bad_formatting,
    #         )
    #         """
    #     )
    #
    #     namespaces = [
    #         ("something.parse.etc", "etc.dedicated.namespace"),
    #         ("something.parse.bad_formatting", "a_new.namespace_here"),
    #     ]
    #
    #     expected = textwrap.dedent(
    #         """\
    #         from a_new import namespace_here as whatever
    #         from etc.dedicated import namespace
    #         from something.parse import (
    #             bazz,
    #             another_line as thing,
    #         )
    #         """
    #     )
    #
    #     self._test(expected, code, namespaces, partial=False)

    def test_star(self):
        """Replace a star-import."""
        code = "from foo import *"
        namespaces = [("foo.bar", "something.parse")]
        expected = "from something import *"

        self._test(expected, code, namespaces, partial=True)

    def test_complex_partial(self):
        """Check that difficult formatting still replaces the imports, correctly."""
        code = textwrap.dedent(
            """\
            from foo.more import (
                blah as whatever, bazz,
                etc,
                another_line as thing,
                    bad_formatting
            )
            """
        )
        namespaces = [
            ("foo.more.another_line", "new.namespace.new_name"),
            ("foo.more.etc", "new.namespace.etc"),
        ]
        expected = textwrap.dedent(
            """\
            from new.namespace import (
                blah as whatever, bazz,
                etc,
                new_name as thing,
                    bad_formatting
            )
            """
        )

        self._test(expected, code, namespaces, partial=True)

    def test_backslash_001(self):
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

    def test_backslash_002(self):
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

    def test_backslash_003(self):
        """Replace imports with backslashes."""
        code = textwrap.dedent(
            """\
            import os.path, \\
                    textwrap \\
                another
            """
        )

        namespaces = [("textwrap", "thing")]

        expected = textwrap.dedent(
            """\
            import os.path, \\
                    thing \\
                another
            """
        )

        self._test(expected, code, namespaces, partial=False)

    def test_backslash_004(self):
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

    def test_from_backslash_001(self):
        """Replace imports with backslashes."""
        code = textwrap.dedent(
            """\
            from thing import path, \\
                textwrap
            """
        )

        namespaces = [("thing.textwrap", "blah.another")]

        expected = textwrap.dedent(
            """\
            from blah import path, \\
                another
            """
        )

        self._test(expected, code, namespaces, partial=True)

    def test_from_backslash_002(self):
        """Replace imports with backslashes."""
        code = textwrap.dedent(
            """\
            from blah import path, \\
                    textwrap
            """
        )

        namespaces = [("blah.path", "another.thingy")]

        expected = textwrap.dedent(
            """\
            from another import thingy, \\
                    textwrap
            """
        )

        self._test(expected, code, namespaces, partial=True)

        expected = textwrap.dedent(
            """\
            from another import thingy
            from blah import \\
                    textwrap
            """
        )

        self._test(expected, code, namespaces, partial=False)

    def test_from_backslash_003(self):
        """Replace imports with backslashes."""
        code = textwrap.dedent(
            """\
            from mit import path, \\
                    textwrap \\
                another
            """
        )

        namespaces = [("mit.textwrap", "cornell.thing")]

        expected = textwrap.dedent(
            """\
            from cornell import path, \\
                    thing \\
                another
            """
        )

        self._test(expected, code, namespaces, partial=True)


class PartialFrom(_Common):
    """Control when and how "from X import Y" imports are replaced."""

    def test_off_full(self):
        """If the namespaces fully describes an import, replace it no matter what."""
        code = "from foo.block.items import another, thing"
        namespaces = [
            ("foo.block.items.another", "blah.items.another"),
            ("foo.block.items.thing", "blah.items.thing"),
        ]
        expected = "from blah.items import another, thing"

        self._test(expected, code, namespaces, partial=False)

    def test_off_partial_001(self):
        """Block a replace because the old namespace is not fully defined."""
        code = "from foo.block.items import another"
        namespaces = [("foo.block", "blah")]
        expected = code

        self._test(expected, code, namespaces, partial=False)

    def test_off_partial_002(self):
        """Block a replace because the old namespace is not fully defined."""
        code = "from foo.block.items import another, thing"
        namespaces = [("foo.block", "blah")]
        expected = code

        self._test(expected, code, namespaces, partial=False)

    def test_off_partial_003(self):
        """Block replacement even if the namespace describes the full "from X" part."""
        code = "from foo.block.items import another"
        namespaces = [("foo.block.items", "blah")]
        expected = code

        self._test(expected, code, namespaces, partial=False)

    def test_on_full(self):
        """If the namespaces fully describes an import, replace it no matter what."""
        code = "from foo.block.items import another, thing"
        namespaces = [
            ("foo.block.items.another", "blah.items.another"),
            ("foo.block.items.thing", "blah.items.thing"),
        ]
        expected = "from blah.items import another, thing"

        self._test(expected, code, namespaces, partial=True)

    def test_on_partial_001(self):
        """Allow replacement even if only part of the "from X" import is defined."""
        code = "from foo.block.items import another"
        namespaces = [("foo.block", "blah")]
        expected = "from blah.items import another"

        self._test(expected, code, namespaces, partial=True)

    def test_on_partial_002(self):
        """Allow replacement even if "from X" isn't fully defined in a multi-import."""
        code = "from foo.block.items import another, thing"
        namespaces = [("foo.block", "blah")]
        expected = "from blah.items import another, thing"

        self._test(expected, code, namespaces, partial=True)

    def test_replace_indentation(self):
        """Make sure replacing import doesn't cause indentation issues."""
        code = textwrap.dedent(
            """\
            if True:
                from foo.block.items import another, thing

                    if True:
                        import foo.bar.bazz

                if False:
                    import something_else
            """
        )

        namespaces = [
            ("foo.block", "blah"),
            ("something_else", "new"),
        ]
        expected = textwrap.dedent(
            """\
            if True:
                from blah.items import another, thing

                    if True:
                        import foo.bar.bazz

                if False:
                    import new
            """
        )

        self._test(expected, code, namespaces, partial=True)

    def test_split_001(self):
        """If you describe one namespace of an import but not the other, make another import."""
        code = "from foo.block.items import another, thing"
        namespaces = [("foo.block.items.another", "blah.another")]
        expected = textwrap.dedent(
            """\
            from blah import another
            from foo.block.items import thing"""
        )

        self._test(expected, code, namespaces, partial=False)
        expected = "from blah import another, thing"
        self._test(expected, code, namespaces, partial=True)

    def test_split_002(self):
        """If you describe one namespace of an import but not the other, make another import."""
        code = "from foo.block.items import another, thing"
        namespaces = [("foo.block.items.another", "blah.blarg.another")]
        expected = textwrap.dedent(
            """\
            from blah.blarg import another
            from foo.block.items import thing"""
        )

        self._test(expected, code, namespaces, partial=False)
        expected = "from blah.blarg import another, thing"
        self._test(expected, code, namespaces, partial=True)

    def test_split_003_indentation(self):
        """If you describe one namespace of an import but not the other, make another import."""
        code = textwrap.dedent(
            """\
            if True:
                from foo.block.items import another, thing
            """
        )
        namespaces = [("foo.block.items.another", "blah.blarg.another")]
        expected = textwrap.dedent(
            """\
            if True:
                from blah.blarg import another
                from foo.block.items import thing
            """
        )

        self._test(expected, code, namespaces, partial=False)
        expected = textwrap.dedent(
            """\
            if True:
                from blah.blarg import another, thing
            """
        )
        self._test(expected, code, namespaces, partial=True)

    def test_alias_001(self):
        """Split an aliases from-import into its own separate import."""
        code = "from foo.block.items import another as more, thing"
        namespaces = [("foo.block.items.another", "blah.another")]
        expected = textwrap.dedent(
            """\
            from blah import another as more
            from foo.block.items import thing"""
        )

        self._test(expected, code, namespaces, partial=False)
        expected = "from blah import another as more, thing"
        self._test(expected, code, namespaces, partial=True)

    def test_alias_002(self):
        """Split an aliases from-import into its own separate import."""
        code = "from foo.block.items import another as more, thing"
        namespaces = [("foo.block.items.another", "blah.something_else")]
        expected = textwrap.dedent(
            """\
            from blah import something_else as more
            from foo.block.items import thing"""
        )

        self._test(expected, code, namespaces, partial=False)
        expected = "from blah import something_else as more, thing"
        self._test(expected, code, namespaces, partial=True)


class PartialImport(_Common):
    """Control when and how "import X" imports are replaced."""

    def test_single(self):
        """Don't split anything because the namespace is described."""
        code = "import foo, bar"
        namespaces = [("foo", "new")]
        expected = "import new, bar"

        self._test(expected, code, namespaces, partial=False)
        self._test(expected, code, namespaces, partial=True)

    def test_multiple(self):
        """Don't split anything and keep it all in one import."""
        code = "import foo.blah, thing.another, fire.water"
        namespaces = [("foo.blah", "new.blah"), ("fire.water", "new.water")]
        expected = "import new.blah, thing.another, new.water"

        self._test(expected, code, namespaces, partial=False)
        self._test(expected, code, namespaces, partial=True)

        namespaces = [("foo.blah", "new.blah"), ("fire.water", "something.water")]
        expected = "import new.blah, thing.another, something.water"

        self._test(expected, code, namespaces, partial=False)
        self._test(expected, code, namespaces, partial=True)

    def test_mixed(self):
        """Try to replace nested and non-nested namespaces whenever possible."""
        code = "import foo.blah, thing.another, foo"
        namespaces = [("foo", "module")]
        expected = "import foo.blah, thing.another, module"

        self._test(expected, code, namespaces, partial=False)

        expected = "import module.blah, thing.another, module"

        self._test(expected, code, namespaces, partial=True)

    def test_partial_001(self):
        """Don't split any namespaces because every replaced namespace is 100% described."""
        code = "import foo.blah, thing.another, fire.water"
        namespaces = [("foo.blah", "new.blah"), ("fire.water", "earth.water")]
        expected = "import new.blah, thing.another, earth.water"

        self._test(expected, code, namespaces, partial=False)
        self._test(expected, code, namespaces, partial=True)

    def test_partial_002(self):
        """Split only certain namespaces when partial is True or False."""
        code = "import foo.blah, thing.another, foo.blah.more"
        namespaces = [("foo.blah", "new.blah")]
        expected = "import new.blah, thing.another, foo.blah.more"

        self._test(expected, code, namespaces, partial=False)

        expected = "import new.blah, thing.another, new.blah.more"

        self._test(expected, code, namespaces, partial=True)
