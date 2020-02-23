"""Add Python 2 / 3 mapping for the io.StringIO class."""

import six

six.add_move(six.MovedModule("io", "StringIO", "io"))
