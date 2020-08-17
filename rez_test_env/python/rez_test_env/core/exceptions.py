#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""All exceptions for `rez_test_env` to use in the CLI.

When user-specific issues while using the CLI occur, these exceptions
are raised.

"""

class MissingTests(Exception):
    """Whenever the user provides 1+ Rez test name that does not exist."""

    pass


class NoValidPackageFound(Exception):
    """Whenever the user provides a Rez package/version that does not exist."""

    pass
