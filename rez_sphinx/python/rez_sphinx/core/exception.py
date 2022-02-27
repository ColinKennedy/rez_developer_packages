"""All exceptions needed by :ref:`rez_sphinx` for internal use.

These exceptions are not meant for any third-party package to import or use.

"""

class NoPackageFound(Exception):
    """If a Rez package is needed but none can be found."""

    pass
