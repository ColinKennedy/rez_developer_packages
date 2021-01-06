"""A series of modules for making Python packages Python-2 and 3 compatible."""

import six

six.add_move(six.MovedModule("io", "StringIO", "io"))
# Make mock importable in Python 2 and 3. `from six.moves import mock`
six.add_move(six.MovedModule("mock", "mock", "unittest.mock"))
