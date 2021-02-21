#!/usr/bin/env python
# -*- coding: utf-8 -*-

import textwrap

from . import common


class Imports(common.Common):
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
            ("something", "something"),
            ("something.blah", "thing.another.blah"),
            ("something.another", "thing.another.another"),
        ]
        expected = textwrap.dedent(
            """\
            from thing import another
            import something

            def foo():
                def bar():

                    another.blah
                    another.another()
            """
        )

        self._test(expected, code, namespaces, partial=True)

    # TODO : Add replace checks for `from imports, too`
    # def test_inner(self):
    #     """Replace an import and its function caller names."""
    #     code = textwrap.dedent(
    #         """\
    #         import something
    #
    #         something.blah
    #         something.inner_function()
    #         """
    #     )
    #     namespaces = [
    #         ("something.blah", "another.blah"),
    #         ("something.inner_function", "another.get_foo"),
    #     ]
    #     expected = textwrap.dedent(
    #         """\
    #         import another
    #
    #         another.blah
    #         another.get_foo()
    #         """
    #     )
    #
    #     self._test(expected, code, namespaces, partial=True)

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
            ("something", "something"),
            ("something.blah", "thing.another.blah"),
            ("something.another", "thing.another.another"),
        ]
        expected = textwrap.dedent(
            """\
            from thing import another
            import something

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
            ("something", "something"),
            ("something.blah", "thing.another.blah"),
            ("something.another", "thing.another.another"),
        ]
        expected = textwrap.dedent(
            """\
            from thing import another
            import something

            another.blah
            another.another()
            """
        )

        self._test(expected, code, namespaces, partial=True)

    # TODO : Add nested checks (check within function, within class, nested, etc
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
            ("something", "something"),
            ("something.blah", "another2.blah"),
            ("something.inner_function", "another2.get_inner"),
        ]
        expected = textwrap.dedent(
            """\
            import another2
            import something

            blah.blah(inner[another2.get_inner()])
            a_module.SomeClass.class_method(
                thing,
                another,
                another2.blah,
            )
            """
        )

        self._test(expected, code, namespaces, partial=True)

    # def test_nested_dots(self):
    #     """Don't replace code if it is nested under a different parent namespace."""
    #     code = textwrap.dedent(
    #         """\
    #         import something
    #
    #         blah.blah.something.inner_function()
    #         thing.another.something.blah
    #         thing.another.something.blah(
    #             thing,
    #             another,
    #             something.blah[1 + index],
    #         )
    #         """
    #     )
    #     namespaces = [
    #         ("something.blah", "another2.blah"),
    #         ("something.inner_function", "another2.get_inner"),
    #     ]
    #     expected = textwrap.dedent(
    #         """\
    #         import another2
    #
    #         blah.blah.something.inner_function()
    #         thing.another.something.blah
    #         thing.another.something.blah(
    #             thing,
    #             another,
    #             another2.blah[1 + index],
    #         )
    #         """
    #     )
    #
    #     self._test(expected, code, namespaces)
