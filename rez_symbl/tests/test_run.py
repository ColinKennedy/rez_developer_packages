#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Run ``rez_symbl`` and make sure its CLI works as-expected."""

import os

from python_compatibility.testing import common
from rez_symbl.core import linker


class Api(common.Common):
    """Check that functions in :mod:`rez_symbl.api` work as expected."""

    def test_bad_resolve(self):
        """If the user provides 1+ packages which don't exist, raise a ValueError."""
        with self.assertRaises(ValueError):
            linker.bake_from_request(
                ["some_package_that_does_not_exist"], "/some/folder",
            )

    def test_not_in_rez_environment(self):
        """If the user is not in a Rez-resolved environment."""
        os.environ.clear()

        with self.assertRaises(EnvironmentError):
            linker.bake_from_current_environment("/some/folder")
