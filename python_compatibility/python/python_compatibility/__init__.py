"""A series of modules for making Python packages Python-2 and 3 compatible."""

import six

six.add_move(six.MovedModule('io', 'StringIO', 'io'))
