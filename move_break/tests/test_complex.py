#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Test the limit of the refactoring logic. Try to break it as much as possible."""

import textwrap

from . import common


class DotHell(common.Common):
    """Replace everything you can, and nothing else."""

    def test_extended_namespace(self):
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

    def test_namespace_within_namespace_callable(self):
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
