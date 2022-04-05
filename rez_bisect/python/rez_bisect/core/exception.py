class Base(Exception):
    pass


class BadRequest(Base):
    pass


class DuplicateContexts(Base):
    """When 2 unique Rez :ref:`contexts` are expected but only one is found."""
    pass


class FileNotFound(Base):
    pass


class PermissionsError(Base):
    pass


class UserInputError(Base):
    pass
