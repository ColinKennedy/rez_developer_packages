#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Make sure replacing classes, attributes, and variables works as expected."""

import textwrap

from . import common


# TODO : Add a from import and import which uses commas!
# TODO : A nested index , dict, etc thing
# TODO : make sure that nested attributes replace correctly (e.g. "foo.bar.MyClass.thing"
# TODO : Check if if I need to add `partial=False` to any of these tests
class Imports(common.Common):
    """Make sure replacing classes, attributes, and variables works as expected."""

    def test_bracket_expressions_001(self):
        """Replace name references within []s and {}s."""
        code = textwrap.dedent(
            """\
            from more import things
            import something

            something.inner.key_1 = {
                "asdfasdf": more.things.here(something.key_1()),
            }
            """
        )

        namespaces = [
            ("import:more.things", "import:newer_place.bar"),
            ("import:something", "import:another"),
        ]

        expected = textwrap.dedent(
            """\
            from newer_place import bar
            import another

            another.inner.key_1 = {
                "asdfasdf": bar.here(another.key_1()),
            }
            """
        )

        self._test(expected, code, namespaces, partial=True)

    def test_bracket_expressions_002(self):
        """Replace name references within []s and {}s."""
        code = textwrap.dedent(
            """\
            from more import things
            import something

            something.key_1["tt"] = {
                "asdfasdf": more.things.here(something.key_1),
            }
            """
        )

        namespaces = [
            ("import:more.things", "import:newer_place.bar"),
            ("import:something", "import:another"),
        ]

        expected = textwrap.dedent(
            """\
            from newer_place import bar
            import another

            another.key_1["tt"] = {
                "asdfasdf": bar.here(another.key_1),
            }
            """
        )

        self._test(expected, code, namespaces, partial=True)

    def test_complex(self):
        """Replace name references inside nested Python syntax."""
        code = textwrap.dedent(
            """\
            something.key_1 = {
                "asdfasdf": (
                            ['blah.blah', more.things.here(
                                    something.key_1,
                            ),

                            {
                                something.key_3: 8 + "expression" + third_party.MyKlass() + \
                                    inner.place['blah':'fizz']
                            }
                        ]
                ),
            }
            """
        )

        namespaces = [
            ("import:more.things", "import:newer_place"),
            ("import:more.things.inner", "import:somewhere_else"),
            ("import:something", "import:another"),
            ("import:third_party", "import:new_zone.core"),
            ("more.things.inner.place", "somewhere_else.blah"),
            ("something.key_1", "another.key_x"),
            ("something.key_3", "new_zone.core.blah"),
            ("third_party.MyKlass", "new_zone.core.MyClass"),
        ]

        expected = textwrap.dedent(
            """\
            from new_zone import core
            import another
            import somewhere_else
            import newer_place
            another.key_x = {
                "asdfasdf": (
                            ['blah.blah', more.things.here(
                                    another.key_x,
                            ),

                            {
                                core.blah: 8 + "expression" + core.MyClass() + \
                                    somewhere_else.blah['blah':'fizz']
                            }
                        ]
                ),
            }
            """
        )

        self._test(expected, code, namespaces, partial=False)

    def test_function(self):
        """Replace a name reference within functions."""
        code = textwrap.dedent(
            """\
            import something

            def foo():
                def bar():

                    something.blah
                    something.another()
            """
        )
        namespaces = [
            ("import:something", "import:another"),
            ("something.blah", "another.blah"),
            ("something.another", "another.another"),
        ]
        # TODO : Make it so there's no redundant imports, later
        expected = textwrap.dedent(
            """\
            import another

            def foo():
                def bar():

                    another.blah
                    another.another()
            """
        )

        self._test(expected, code, namespaces, partial=True)

    def test_keep_import_001(self):
        """Don't replace an import if it is still in-use in the module."""
        code = textwrap.dedent(
            """\
            from something import parse

            parse.foo
            parse.bar
            """
        )
        namespaces = [
            ("import:something.parse", "import:blah.another"),
            ("something.parse.foo", "blah.another.thing"),
        ]
        expected = textwrap.dedent(
            """\
            from blah import another
            from something import parse

            another.thing
            parse.bar
            """
        )

        self._test(expected, code, namespaces, partial=False)

    def test_keep_import_002(self):
        """Don't replace an import if it is still in-use in the module."""
        code = textwrap.dedent(
            """\
            import parse

            parse.foo
            parse.bar
            """
        )
        namespaces = [
            ("import:parse", "import:another"),
            ("parse.foo", "another.thing"),
        ]
        expected = textwrap.dedent(
            """\
            import another
            import parse

            another.thing
            parse.bar
            """
        )

        self._test(expected, code, namespaces, partial=False)

    def test_keep_import_003(self):
        """Don't replace an import if it is still in-use in the module."""
        code = textwrap.dedent(
            """\
            from something import parse as testout

            testout.foo
            testout.bar
            """
        )
        namespaces = [
            ("import:something.parse", "import:blah.another"),
            ("something.parse.foo", "blah.another.thing"),
        ]
        expected = textwrap.dedent(
            """\
            from blah import another
            from something import parse as testout

            another.thing
            testout.bar
            """
        )

        self._test(expected, code, namespaces, partial=False)

    def test_keep_import_003b(self):
        """Don't replace an import if it is still in-use in the module."""
        code = textwrap.dedent(
            """\
            import something as testout

            testout.foo
            testout.bar
            """
        )
        namespaces = [
            ("import:something", "import:blah"),
            ("something.foo", "blah.thing"),
        ]
        expected = textwrap.dedent(
            """\
            import blah
            import something as testout

            blah.thing
            testout.bar
            """
        )

        self._test(expected, code, namespaces, partial=False)

    def test_keep_import_004(self):
        """Don't replace an import if it is still in-use in the module."""
        code = textwrap.dedent(
            """\
            from something import parse
            from something import parse as testout

            parse.foo
            parse.bar
            testout.foo
            testout.bar
            """
        )
        namespaces = [
            ("import:something.parse", "import:blah.another"),
            ("something.parse.foo", "blah.another.thing"),
        ]
        expected = textwrap.dedent(
            """\
            from blah import another
            from something import parse
            from something import parse as testout

            another.thing
            parse.bar
            another.thing
            testout.bar
            """
        )

        self._test(expected, code, namespaces, partial=False)

    def test_method(self):
        """Replace a name reference within class methods."""
        code = textwrap.dedent(
            """\
            import something

            def foo():

                class Inner(object):

                    thing = something.blah

                    def _something(self):
                        something.another()
            """
        )
        namespaces = [
            ("import:something", "import:thing.another"),
            ("something.blah", "thing.another.blah"),
            ("something.another", "thing.another.another"),
        ]
        expected = textwrap.dedent(
            """\
            from thing import another

            def foo():

                class Inner(object):

                    thing = another.blah

                    def _something(self):
                        another.another()
            """
        )

        self._test(expected, code, namespaces, partial=True)

    def test_module_001(self):
        """Replace a basic, minimum import and a name reference."""
        code = textwrap.dedent(
            """\
            import something

            something.blah
            something.another()
            """
        )
        namespaces = [
            ("import:something", "import:thing.another"),
            ("something.blah", "thing.another.blah"),
            ("something.another", "thing.another.another"),
        ]
        expected = textwrap.dedent(
            """\
            from thing import another

            another.blah
            another.another()
            """
        )

        self._test(expected, code, namespaces, partial=True)

    def test_nested_caller(self):
        """Replace an import and names within a nested expression."""
        code = textwrap.dedent(
            """\
            import something

            blah.blah(inner[something.inner_function()])
            a_module.SomeClass.class_method(
                thing,
                another,
                something.blah,
            )
            """
        )
        namespaces = [
            ("import:something", "import:another2"),
            ("something.blah", "another2.blah"),
            ("something.inner_function", "another2.get_inner"),
        ]
        expected = textwrap.dedent(
            """\
            import another2

            blah.blah(inner[another2.get_inner()])
            a_module.SomeClass.class_method(
                thing,
                another,
                another2.blah,
            )
            """
        )

        self._test(expected, code, namespaces, partial=True)

    def test_nested_dots(self):
        """Don't replace code if it is nested under a different parent namespace."""
        code = textwrap.dedent(
            """\
            import something

            blah.blah.something.inner_function()
            thing.another.something.blah
            thing.another.something.blah(
                thing,
                another,
                something.blah[1 + index],
            )
            """
        )
        namespaces = [
            ("import:something", "import:another2"),
            ("something.blah", "another2.blah"),
            ("something.inner_function", "another2.get_inner"),
        ]
        expected = textwrap.dedent(
            """\
            import another2

            blah.blah.something.inner_function()
            thing.another.something.blah
            thing.another.something.blah(
                thing,
                another,
                another2.blah[1 + index],
            )
            """
        )

        self._test(expected, code, namespaces, partial=True)
