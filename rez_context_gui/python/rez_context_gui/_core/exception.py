"""All exceptions used internally by :mod:`rez_context_gui`.

These exceptions are mostly just to make the CLI more readable. They aren't
meant to be imported / used by other Rez packages.

"""


class Base(Exception):
    """An exception that other classes must inherit from."""

    code = 1


class ContextNotFound(Base):
    """If Rez context is needed but cannot be found."""

    code = 10


class InvalidContext(Base):
    """If Rez context is needed but it is invalid."""

    code = 20
