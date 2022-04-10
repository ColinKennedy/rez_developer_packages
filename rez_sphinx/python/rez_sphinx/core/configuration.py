"""A wrap for accessing data from `Sphinx conf.py`_, from `Sphinx`_."""

import importlib
import inspect
import logging
import os
import pkgutil

from python_compatibility import imports, wrapping
from six.moves import mock
from sphinx import builders, config

from . import constant

_LOGGER = logging.getLogger(__name__)


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
            ConfPy: The created instance.

        """
        return cls.from_path(os.path.join(directory, constant.SPHINX_CONF_NAME))

    @classmethod
    def from_path(cls, path):
        """Convert a file path into an instance.

        Args:
            path (str): The absolute path to a file or folder on-disk.

        Raises:
            IOError:

        Returns:
            ConfPy: The converted instance.

        """
        if not os.path.isfile(path):
            raise IOError(
                'Path "{path}" does not exist and cannot be imported.'.format(path=path)
            )

        module = imports.import_file("rez_sphinx_conf", path)

        return cls(module)

    @staticmethod
    def is_valid_directory(directory):
        """Check if ``directory`` has a configuration file that this class can load.

        Args:
            directory (str): The absolute or relative folder path on-disk.

        Returns:
            bool: If the configuration can be read, return True.

        """
        return os.path.isfile(os.path.join(directory, constant.SPHINX_CONF_NAME))

    def _get_extensions(self):
        """list[str]: Get each Python importable module that `Sphinx`_ will load."""
        if not hasattr(self._module, "extensions"):
            return []

        return getattr(self._module, "extensions")

    def _get_master_doc(self):
        """str: Get the name of the documentation "front page" file."""
        try:
            return self._module.master_doc
        except AttributeError:
            return "index"  # A reasonable default

    def get_attributes(self, allow_extensions=True):
        """Get each found attribute and its values.

        Args:
            allow_extensions (bool, optional):
                If True, include `Sphinx`_ extension attributes, like
                `intersphinx_mapping`_. If False, only return the base
                `Sphinx`_ attributes and nothing else.

        Returns:
            dict[tuple[str], object]: The found attribute and its value.

        """
        names = self.get_known_attribute_names(allow_extensions=allow_extensions)

        return {
            name: getattr(self._module, name)
            for name in names
            if hasattr(self._module, name)
        }

    def get_extensions(self):
        """Get all registered `Sphinx`_ extensions. e.g. `sphinx.ext.viewcode`_.

        Returns:
            list[str]: The registered extensions.

        """
        return self._module.extensions or []

    def get_known_attribute_names(self, allow_extensions=True):
        """Find every `Sphinx conf.py`_ attribute.

        Args:
            allow_extensions (bool, optional):
                If True, include `Sphinx`_ extension attributes, like
                `intersphinx_mapping`_. If False, only return the base
                `Sphinx`_ attributes and nothing else.

        Returns:
            set[str]: Each found attribute name.

        """
        output = set(config.Config.config_values.keys())

        if allow_extensions:
            extensions = self._get_extensions()
            modules = _get_modules_from_namespace(extensions)
            output.update(_get_extension_attribute_names(modules))

        output.update(_get_known_builder_attribute_names())

        return output

    def get_master_document_path(self):
        """str: Get the full path on-disk where this `Sphinx conf.py`_ lives."""
        name = self._get_master_doc() + self.get_source_extension()

        return os.path.join(self._directory, name)

    def get_source_extension(self):
        """str: Get the extension to search for ReST files."""
        try:
            return self._module.source_suffix
        except AttributeError:
            return constant.SOURCE_DOCUMENTATION_EXTENSION  # A reasonable default

    def get_module_path(self):
        """str: Get the full path to this `Sphinx conf.py`_ file, on-disk."""
        return self._module.__file__


def _get_extension_attribute_names(modules):
    """Find every attribute for each `Sphinx`_ extension in ``modules``.

    Args:
        modules (iter[module]):
            An importable Python namespace to try to get attribute contents from.

    Returns:
        set[str]: Every found attribute name across all extensions.

    """

    def _capture_value(appender):
        def _wrap(attribute_name, *_, **__):
            appender(attribute_name)

        return _wrap

    # Since `Sphinx`_ requires a ``setup`` function on every extension module
    # which defines attributes, we take advantage of this convention by passing
    # a fake ``app`` variable and returning its accumulated results.
    #
    # Simple but effective.
    #
    container = set()
    mocker = mock.MagicMock()
    mocker.add_config_value = _capture_value(container.add)

    for module in modules:
        if hasattr(module, "setup"):
            with wrapping.silence_printing():  # Sphinx can be rather spammy.
                module.setup(mocker)

    return container


def _get_known_builder_attribute_names():
    """set[str]: Find all attributes which come from `Sphinx`_ builder modules."""
    # Reference: https://stackoverflow.com/a/1707786/3626104
    prefix = builders.__name__ + "."

    modules = [
        importlib.import_module(namespace)
        for _, namespace, _ in pkgutil.iter_modules(
            builders.__path__,
            prefix,
        )
    ]

    return _get_extension_attribute_names(modules)


def _get_modules_from_namespace(namespaces):
    """Convert fully-qualified Python importable namespaces into modules.

    Args:
        namespaces (iter[str]):
            Each importable Python namespace to try to import.
            e.g. ``["sphinx.ext.intersphinx", "sphinx.ext.viewcode"]``.

    Returns:
        list[module]: The imported modules.

    """
    modules = []

    for name in namespaces:
        _LOGGER.debug('Now importing "%s" to query its attributes.', name)

        try:
            modules.append(importlib.import_module(name))
        except Exception as error:  # pylint: disable=broad-except
            # We're importing arbitrary Python modules based on whatever the
            # user has set.  So we need to catch generalized errors.
            #
            _LOGGER.warning('Skipped loading "%s". Error, "%s".', name, str(error))

            continue

    return modules
