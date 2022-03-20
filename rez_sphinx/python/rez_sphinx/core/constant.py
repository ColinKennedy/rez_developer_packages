"""Any variables needed by other modules within :ref:`rez_sphinx`.

Attributes:
    REZ_SPHINX_OBJECTS_INV (str):
        A key needed by Sphinx, internally, in order to load `objects.inv`_
        files. This key is auto-added to Rez packages on-build.
    ROOT_REPLACEMENT (str):
        A string to search for and replace while modifying the user's `help`_
        entries. This later may be replaced with a website address or a local
        Rez package path so users can find the documentation more easily.

"""

REZ_SPHINX_OBJECTS_INV = "rez_sphinx objects.inv"
ROOT_REPLACEMENT = "{root}"
