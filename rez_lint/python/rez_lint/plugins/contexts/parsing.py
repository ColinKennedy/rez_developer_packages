#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Heavy processing like parsing Python files take place in this module."""

import parso

from ...core import lint_constant
from . import base_context


class ParsePackageDefinition(base_context.BaseContext):
    """Use :mod:`parso` to tokenize and parse a the Rez package.py file.

    This checker assumes that the user is using "package.py". Other standards
    like "package.yaml" are ignored.

    """

    @staticmethod
    def run(package, context):
        """Parse `package` into parso nodes and add the entire module into `context`.

        Args:
            package (:class:`rez.packages_.DeveloperPackage`):
                The Rez package that will get parsed.
            context (:class:`.Context`):
                A data instance that will stored the parsed output.

        """
        path = package.filepath

        if not path.endswith(".py"):
            return

        with open(path, "r") as handler:
            code = handler.read()

        context[lint_constant.PARSO_GRAPH] = parso.parse(code)
