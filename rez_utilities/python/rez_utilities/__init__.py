"""Helper modules for developing tools, using Rez."""

import six

# Fix the compatibility issue between Python 2 and Python 3, using `six.moves.io`
six.add_move(six.MovedModule("io", "StringIO", "io"))
