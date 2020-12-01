#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""All exceptions for `rez_test_env` to use in the CLI.

When user-specific issues while using the CLI occur, these exceptions
are raised.

"""


class _Base(Exception):
    """A class for all other exceptions to inherit from."""

    pass


class MissingTests(_Base):
    """Whenever the user provides 1+ Rez test name that does not exist."""

    pass


class ConflictingArguments(_Base):
    """If the user provides arguments to the CLI which aren't allowed.

    Example:
        You cannot provide a package_request and --use-pwd at the same time.

    """

    pass


class NoValidPackageFound(_Base):
    """Whenever the user provides a Rez package/version that does not exist."""

    pass
