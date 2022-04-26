"""Any exceptions needed internally by :ref:`rez_docbot <rez_docbot>`."""


class CoreException(Exception):
    """The class which all exceptions in this module most inherit from."""


class MissingDocumentation(CoreException):
    """If the built documentation to publish is missing."""


class NoRemoteFound(CoreException):
    """If a remote git repository was needed / excepted but none was found."""
