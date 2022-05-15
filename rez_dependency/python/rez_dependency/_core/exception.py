"""Some private, common exceptions to make the CLI a bit easier to understand."""


class Base(Exception):
    """The class for other exceptions to inherit."""

    code = 1


class InvalidContext(Base):
    """If a valid Rez context could not be created / constructed."""

    code = 10


class NoPackage(Base):
    """If an expected Rez package (source or installed) could not be found."""

    code = 20


class UserInputError(Base):
    """When a user's CLI input has some wort of problem."""

    code = 30
