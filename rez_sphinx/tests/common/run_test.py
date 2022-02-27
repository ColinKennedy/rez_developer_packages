import shlex

import six
from rez_sphinx import cli


def test(text):
    parts = text

    if isinstance(parts, six.string_types):
        parts = shlex.split(parts)

    cli.main(parts)
