"""A wrap for accessing data from `Sphinx conf.py`_, from `Sphinx`_."""

import functools
import inspect
import os

from python_compatibility import imports
from sphinx.ext import intersphinx
from sphinx import config
from six.moves import mock

_CONFIGURATION_FILE_NAME = "conf.py"


class ConfPy(object):
    """A wrap for accessing data from `Sphinx conf.py`_, from `Sphinx`_."""

    def __init__(self, module):
        """Keep track of a `Sphinx conf.py`_ module.

        Args:
            module (module): The Python `Sphinx conf.py`_ to keep.

        """
        super(ConfPy, self).__init__()

        self._module = module
        self._directory = os.path.dirname(inspect.getsourcefile(self._module))

    @classmethod
    def from_directory(cls, directory):
        """Find and convert a `Sphinx conf.py`_ located directly within ``directory``.

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
        """Get all registered `Sphinx`_ extensions. e.g. `sphinx.ext.viewcode`_.

        Returns:
            list[str]: The registered extensions.

        """
        return self._module.extensions or []

    def get_master_document_path(self):
        """str: Get the full path on-disk where this `Sphinx conf.py`_ lives."""
        name = self._get_master_doc() + self.get_source_extension()

        return os.path.join(self._directory, name)

    def get_source_extension(self):
        """str: Get the extension to search for ReST files."""
        try:
            return self._module.source_suffix
        except AttributeError:
            return ".rst"  # A reasonable default

    def get_module_attributes(self):
        base_sphinx_attributes = [
            (name, getattr(self._module, name))
            for name in config.Config.config_values.keys()
            if hasattr(self._module, name)
        ]

        interspinx_attributes = []

        for name in _get_intersphinx_attribute_names():
            if hasattr(self._module, name):
                interspinx_attributes.append((name, getattr(self._module, name)))

        return base_sphinx_attributes + interspinx_attributes

    def get_module_path(self):
        return self._module.__file__


def _get_intersphinx_attribute_names():
    def _capture_value(appender):
        def _wrap(attribute_name, *args, **kwargs):
            appender(attribute_name)

            return None

        return _wrap

    container = set()
    mocker = mock.MagicMock()
    mocker.add_config_value = _capture_value(container.add)
    intersphinx.setup(mocker)

    return container
