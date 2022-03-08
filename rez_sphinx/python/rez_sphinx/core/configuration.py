"""A wrap for accessing data from :ref:`conf.py`, from :ref:`Sphinx`."""

import inspect
import os

from python_compatibility import imports

_CONFIGURATION_FILE_NAME = "conf.py"


class ConfPy(object):
    """A wrap for accessing data from :ref:`conf.py`, from :ref:`Sphinx`."""

    def __init__(self, module):
        """Keep track of a :ref:`conf.py` module.

        Args:
            module (module): The Python :ref:`conf.py` to keep.

        """
        super(ConfPy, self).__init__()

        self._module = module
        self._directory = os.path.dirname(inspect.getsourcefile(self._module))

    @classmethod
    def from_directory(cls, directory):
        """Find and convert a :ref:`conf.py` located directly within ``directory``.

        Args:
            directory (str):
                The absolute path to the documentation source directory,
                within some source Rez package.
                e.g. ``"{rez_root}/documentaion/source"``.

        Returns:
            :class:`ConfPy`: The created instance.

        """
        return cls.from_path(os.path.join(directory, _CONFIGURATION_FILE_NAME))

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

    def get_extensions(self):
        """Get all registered :ref:`Sphinx` extensions. e.g. "sphinx.ext.viewcode".

        Returns:
            list[str]: The registered extensions.

        """
        return self._module.extensions or []

    def get_master_document_path(self):
        """str: Get the full path on-disk where this :ref:`conf.py` lives."""
        name = self._get_master_doc() + self.get_source_extension()

        return os.path.join(self._directory, name)

    def get_source_extension(self):
        """str: Get the extension to search for ReST files."""
        try:
            return self._module.source_suffix
        except AttributeError:
            return ".rst"  # A reasonable default