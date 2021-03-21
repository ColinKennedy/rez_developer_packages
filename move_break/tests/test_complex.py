#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Test the limit of the refactoring logic. Try to break it as much as possible."""

import textwrap

from . import common


class DotHell(common.Common):
    """Replace everything you can, and nothing else."""

    def test_extended_namespace(self):
        """Replace the attribute which is nested within an import."""
        code = textwrap.dedent(
            """\
            import os

            os.path.join
            """
        )

        namespaces = [
            ("import:os", "import:another"),
            ("os.path.join", "another.ffff.zzzzz"),
        ]

        expected = textwrap.dedent(
            """\
            import another

            another.ffff.zzzzz
            """
        )

        self._test(expected, code, namespaces, partial=False)

    def test_multi_alias_import_001(self):
        code = textwrap.dedent(
            """\
            from some.base import blah as another

            another.something
            """
        )

        namespaces = [
            ("import:some.base.blah", "import:a_new.place.here"),
            ("some.base.blah.something", "a_new.place.here.namespace"),
        ]

        expected = textwrap.dedent(
            """\
            from a_new.place import here

            here.namespace
            """
        )

        self._test(expected, code, namespaces, partial=True)

    def test_multi_alias_import_001b(self):
        code = textwrap.dedent(
            """\
            from some.base import blah as another

            another.something
            """
        )

        namespaces = [
            ("import:some.base.blah", "import:a_new.place.here"),
            ("some.base.blah.something", "a_new.place.here.namespace"),
        ]

        expected = textwrap.dedent(
            """\
            from a_new.place import here as another

            another.namespace
            """
        )

        self._test(expected, code, namespaces, aliases=True, partial=True)

    def test_multi_alias_import_001c(self):
        code = textwrap.dedent(
            """\
            import thing as another

            another.something
            """
        )

        namespaces = [
            ("import:thing", "import:a_new_place"),
            ("thing.something", "a_new_place.namespace"),
        ]

        expected = textwrap.dedent(
            """\
            import a_new_place as another

            another.namespace
            """
        )

        self._test(expected, code, namespaces, aliases=True, partial=True)

    def test_multi_alias_import_002(self):
        code = textwrap.dedent(
            """\
            from some.base import blah as another, fizz

            another.something
            fizz.maker
            another.not_replaced
            """
        )

        namespaces = [
            ("import:some.base.blah", "import:a_new.place.here"),
            ("some.base.blah.something", "a_new.place.here.namespace"),
        ]

        expected = textwrap.dedent(
            """\
            from a_new.place import here
            from some.base import blah as another, fizz

            here.namespace
            fizz.maker
            another.not_replaced
            """
        )

        self._test(expected, code, namespaces, partial=True)

    def test_multi_alias_import_003(self):
        code = textwrap.dedent(
            """\
            from some.base import blah as another, fizz

            another.something
            fizz.maker
            another.another
            """
        )

        namespaces = [
            ("import:some.base.blah", "import:a_new.place.here"),
            ("some.base.blah.something", "a_new.place.here.namespace1"),
            ("some.base.blah.another", "a_new.place.here.namespace2"),
        ]

        expected = textwrap.dedent(
            """\
            from a_new.place import here
            from some.base import fizz

            here.namespace1
            fizz.maker
            here.namespace2
            """
        )

        self._test(expected, code, namespaces, partial=True)

    def test_alias_import_which_must_split_and_keep(self):
        """Simultaneously "split" and "keep" an aliased from import, based on module attributes.

        This is probably the most complex case for import refactoring.

        """
        code = textwrap.dedent(
            """\
            from some.base import blah as another, fizz, buzz, thing as fff

            another.something
            fizz.maker
            buzz.bee[fff.zzz]
            buzz.bee[fff.mmm]
            another.not_replaced
            """
        )

        namespaces = [
            ("import:some.base.blah", "import:a_new.place.here"),
            ("import:some.base.thing", "import:a_new.place.zoo"),
            ("some.base.blah.something", "a_new.place.here.namespace"),
            ("some.base.thing.zzz", "a_new.place.zoo.zzz"),
            ("some.base.thing.mmm", "a_new.place.zoo.ttt"),
        ]

        expected = textwrap.dedent(
            """\
            from a_new.place import here
            from some.base import blah as another, fizz, buzz, thing as fff

            here.something
            fizz.maker
            buzz.bee[zoo.zzz]
            buzz.bee[zoo.ttt]
            another.not_replaced
            """
        )

        self._test(expected, code, namespaces, partial=True)

    def test_namespace_within_namespace_callable(self):
        """Replace a namespace recursively even if it's a function calling itself."""
        code = textwrap.dedent(
            # Notice, there's no `mock` import. We intentionally leave
            # it out, to try to break this module's replacement
            #
            """\
            if is_static:
                patcher = mock.thing.patch(namespace, blah, mock.thing.patch["asdf"], mock.patch, mock.thing.patch(ff, mock.thing.patch, ttt))
            else:
                patcher = mock.patch(namespace, autospec=True, side_effect=side_effect)
            """
        )

        namespaces = [
            ("import:mock", "import:another"),
            ("mock.thing.patch", "another.ffff.zzzzz"),
        ]

        expected = textwrap.dedent(
            """\
            import another
            if is_static:
                patcher = another.ffff.zzzzz(namespace, blah, another.ffff.zzzzz["asdf"], mock.patch, another.ffff.zzzzz(ff, another.ffff.zzzzz, ttt))
            else:
                patcher = mock.patch(namespace, autospec=True, side_effect=side_effect)
            """
        )

        self._test(expected, code, namespaces, partial=False)
