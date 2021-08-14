"""All tests for the ``rez_package_check`` package and CLI."""

import logging
import sys

import six

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

six.add_move(six.MovedModule("mock", "mock", "unittest.mock"))
