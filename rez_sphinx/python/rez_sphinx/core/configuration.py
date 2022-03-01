"""A wrap for accessing data from :ref:`conf.py`, from :ref:`Sphinx`."""

from python_compatibility import imports


class ConfPy(object):
    """A wrap for accessing data from :ref:`conf.py`, from :ref:`Sphinx`."""

    def __init__(self, module):
        """Keep track of a :ref:`conf.py` module.

        Args:
            module (module): The Python :ref:`conf.py` to keep.

        """
        super(ConfPy, self).__init__()

        self._module = module

    @classmethod
    def from_path(cls, path):
        """Convert a file path into an instance.

        Args:
            path (str): The absolute path to a file or folder on-disk.

        Returns:
            :class:`ConfPy`: The converted instance.

        """
        module = imports.import_file("rez_sphinx_conf", path)

        return cls(module)

    def _get_master_doc(self):
        """str: Get the name of the documentation "front page" file."""
        try:
            return self._module.master_doc
        except AttributeError:
            return "index"  # A reasonable default

    def _get_source_suffix(self):
        """str: Get the extension to search for ReST files."""
        try:
            return self._module.source_suffix
        except AttributeError:
            return ".rst"  # A reasonable default

    def get_master_document_name(self):
        """str: Get the full name of the documentation "front page" file."""
        return self._get_master_doc() + self._get_source_suffix()
