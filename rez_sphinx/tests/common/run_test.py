import shlex

from rez_sphinx import cli


def test(text):
    parts = shlex.split(text)
    cli.main(parts)
