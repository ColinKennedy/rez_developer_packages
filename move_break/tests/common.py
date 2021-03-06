#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""A shared module for the tests in this subfolder."""

import atexit
import functools
import os
import tempfile
import unittest

from move_break import mover


class Common(unittest.TestCase):
    """A base clsas used by other test classes."""

    def _test(  # pylint: disable=too-many-arguments
        self,
        expected,
        code,
        namespaces,
        partial=False,
        aliases=False,
        continue_on_syntax_error=False,
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
            continue_on_syntax_error (bool, optional):
                If True and a path in `files` is an invalid Python module
                and otherwise cannot be parsed then skip the file and keep
                going. Otherwise, raise an exception. Default is False.

        """
        with tempfile.NamedTemporaryFile(
            suffix=".py", mode="w", delete=False
        ) as handler:
            handler.write(code)

        atexit.register(functools.partial(os.remove, handler.name))

        mover.move_imports(
            {handler.name},
            namespaces,
            partial=partial,
            aliases=aliases,
            continue_on_syntax_error=continue_on_syntax_error,
        )

        with open(handler.name, "r") as handler:
            new_code = handler.read()

        raise ValueError(new_code)

        self.assertEqual(expected, new_code)
