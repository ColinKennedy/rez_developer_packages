#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Importing/Modules differ in Python 2 and 3. This module helps with that."""

import importlib
import inspect
import logging
import os

import six

from . import pathrip

_COMMON_IMPORT_EXCEPTIONS = (
    ImportError,  # If the module does not exist
    NameError,  # If the module exists but contains an undefined variable
)
_LOGGER = logging.getLogger(__name__)


def _is_every_inner_folder_importable(directory, root):
    """Check if a sub-directory of another directory describes a Python sub-package.

    Args:
        directory (str):
            The sub-directory of `root` to check. e.g. "/foo/bar/fizz/buzz".
        root (str):
            The top directory that contains `directory`. e.g. "/foo/bar".
            This path is typically a path that you'd add to your PYTHONPATH
            in order to make `directory` importable.

    Returns:
        bool: If `directory` is importable within `root`.

    """
    inner_folders = os.path.relpath(directory, root)
    parts = pathrip.split_os_path_asunder(inner_folders)

    for index in range(len(parts)):
        relative_folder = (os.sep).join(parts[index:])
        package_file = os.path.join(root, relative_folder, "__init__.py")

        if not os.path.isfile(package_file):
            return False

    return True


def _iter_all_namespaces_from_parents(namespace):
    """Get every possible namespace from a given Python dotted-namespace.

    Args:
        namespace (str): The dotted namespace. e.g. "foo.bar.bazz".

    Returns:
        list[str]: All of the possible namespaces. e.g. ["foo.bar.bazz", "foo.bar", "foo"].

    """
    parts = namespace.split(".")

    for index in range(len(parts)):
        if index == 0:
            items = parts
        else:
            items = parts[: -1 * index]

        yield ".".join(items)


def has_importable_module(
    root, ignore=frozenset(), extensions=frozenset((".egg", ".py"))
):
    """Check if a directory has at least one importable Python file / module.

    Args:
        root (str):
            The absolute path to a folder on-disk.
        ignore (set[str], optional):
            If any file path matches one of these options, it will be
            excluded from the checker that this function runs. The
            default ignores nothing.
        extensions (set[str], optional):
            The Python extensions that will be used to check for files.
            Default: {".egg", ".py"}.

    Returns:
        bool: If a module could be found.

    """
    if not os.path.isdir(root):
        return False

    if any(os.path.splitext(name)[-1] in extensions for name in os.listdir(root)):
        return True

    for directory, _, files in os.walk(root):
        for name in files:
            if name in ignore:
                continue

            if os.path.splitext(name)[-1] not in extensions:
                continue

            if _is_every_inner_folder_importable(directory, root):
                return True

    return False


def get_namespace(object_):
    try:
        # Reference: https://www.python.org/dev/peps/pep-3155/
        return object_.__qualname__
    except AttributeError:
        pass

    if inspect.isfunction(object_):
        module = object_.__module__
        name = object_.__name__

        return "{module}.{name}".format(module=module, name=name)

    if inspect.isclass(object_):
        module = object_.__module__
        name = object_.__name__

        return "{module}.{name}".format(module=module, name=name)

    if inspect.ismethod(object_) or type(object_).__name__ == "method-wrapper":
        # method-caller is for "dunder" Python methods, like `__call__`, `__add__`, etc.
        class_ = object_.__self__

        if class_ is None:
            class_ = object_.im_self

        if class_ is None:
            class_ = object_.im_class

        module = class_.__module__

        try:
            class_name = class_.__name__
        except AttributeError:
            class_name = class_.__class__.__name__

        name = object_.__name__

        return "{module}.{class_name}.{name}".format(
            module=module,
            class_name=class_name,
            name=name,
        )

    raise NotImplementedError('Object "{object_}" is not currently supported.'.format(object_=object_))


def get_parent_module(namespace):
    """Get the Python module for the given Python namespace import.

    If the given namespace returns None, there could be several reasons why.

    - It's not in the user's PYTHONPATH
    - The module exists in the PYTHONPATH but it has a SyntaxError or some exception on-import
    - The module is actually a C-binding module (for example) and the C library
      makes the import fail, for some reason.

    Args:
        namespace (str): A dotted Python import path. e.g. "os.path".

    Returns:
        module or NoneType: The found module, if any.

    """
    if not isinstance(namespace, six.string_types):
        _LOGGER.error(
            'Object "%s" is not a string. `get_parent_module` must return Nothing.',
            namespace,
        )

        return None

    if "." not in namespace:
        try:
            return importlib.import_module(namespace)
        except Exception:  # pylint: disable=broad-except
            _LOGGER.warning(
                'Namespace "%s" could not be imported.', namespace, exc_info=True
            )

            return None

    namespaces = list(_iter_all_namespaces_from_parents(namespace))

    for namespace_ in namespaces:
        try:
            module = importlib.import_module(namespace_)
        except Exception:  # pylint: disable=broad-except
            pass
        else:
            _LOGGER.debug('Found module "%s".', namespace_)

            return module

    _LOGGER.warning('Namespaces "%s" could not be imported.', sorted(namespaces))

    return None


def import_nearest_module(namespace):
    """Find a suitable module for some Python namespace.

    Reference:
        https://stackoverflow.com/a/8719100/3626104
        https://stackoverflow.com/a/2725668/3626104

    Args:
        namespace (str):
            A dot-separated string that could be pointing to a Python
            namespace, class, function, or attribute.

    Returns:
        module or NoneType: The found module, if any.

    """
    try:
        return __import__(namespace, fromlist=[""])
    except _COMMON_IMPORT_EXCEPTIONS:
        # Usually happens if the namespace is actually "foo.MyClass" or "foo.my_attribute"
        pass

    while True:
        parts = namespace.split(".")
        parent = parts[:-1]

        if not parent:
            break

        new_namespace = ".".join(parent)

        try:
            return __import__(new_namespace, fromlist=[""])
        except _COMMON_IMPORT_EXCEPTIONS:
            pass

        namespace = new_namespace

    return None


def import_file(namespace, path):
    """Import the given file `path` under the given Python dotted `namespace`.

    Args:
        namespace (str):
            The import namespace. e.g. "foo.bar" might point to a file
            like "/thing/foo/bar.py".
        path (str):
            The absolute path to a Python file to import.

    Returns:
        module: The imported Python code object.

    """
    module = None

    try:
        import importlib.util as _util
    except ImportError:
        pass
    else:
        spec = _util.spec_from_file_location(  # pylint: disable=no-member
            namespace, path
        )
        module = _util.module_from_spec(spec)  # pylint: disable=no-member
        spec.loader.exec_module(module)

        return module

    import imp

    return imp.load_source(namespace, path)
