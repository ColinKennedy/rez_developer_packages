#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Any constants / configuration data that is neede by this package's business logic.

Attributes:
    HAS_PYTHON_PACKAGE (str):
        The key used to store if the found Rez package(s) is defines a
        Python package. The logic that determines this can be very slow
        so, to prevent ``rez_lint`` from running sub-optimally, this key
        is used by a context plugin to run it once and cache the result.

"""

HAS_PYTHON_PACKAGE = "has_python_package"
PARSO_GRAPH = "parso_graph"
