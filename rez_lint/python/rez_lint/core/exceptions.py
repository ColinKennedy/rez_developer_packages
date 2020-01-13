#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""``rez_lint`` specific exceptions."""


class NoPackageFound(Exception):
    """When no Rez packages to linter were found."""

    pass
