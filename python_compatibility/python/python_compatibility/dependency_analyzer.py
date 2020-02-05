#!/usr/bin/env python

"""A tool module that queries Python file dependencies.

Important:
    This module isn't meant to be run directly. It's basically only used
    internally by other Python APIs.

Note:
    This module can only be run when these assumptions are true:

    - This module must be run within a resolved Rez context
    - python_compatibility must be in the user's resolved context along
      with any package that is needed in order to import the found namespaces.
      Otherwise, :func:`_get_source_paths` will return an incomplete list.

"""

import argparse
import imp
import logging
import os
import pkgutil
import sys

import six

from . import filer, import_parser, imports, packaging

_LOGGER = logging.getLogger(__name__)


class _FakeModule(object):
    def __init__(self, path):
        super(_FakeModule, self).__init__()

        if os.path.isdir(path):
            path = os.path.join(path, "__init__.py")

        self._path = path
        self.__file__ = self._path


def _module_has_attribute(module, namespace):
    """Check if a Python module has an attribute/class.

    Args:
        module (module):
            The root that will be used to query attributes and classes.
        namespace (str):
            A dot-separated list of attributes to look up.
            Usually, this will just be a single item such as
            "MyClass" or "my_attribute" but it could also be
            "MyClass.NestedClass.my_attribute".

    Returns:
        bool: If `namespace` is not accessble within `module`.

    """
    inner_namespace = module
    module_directory = os.path.dirname(module.__file__)
    previous_module = module.__file__

    for part in namespace.split("."):
        try:
            inner_namespace = getattr(inner_namespace, part)
        except AttributeError:
            return False

        path = previous_module

        if hasattr(inner_namespace, "__file__"):
            previous_module = inner_namespace.__file__
        else:
            path = previous_module

        if not filer.in_directory(path, module_directory):
            # Normally when an attribute is queried inside of a module,
            # the attribute is literally in that Python file.
            #
            # But because Python supports shared namespaces, this gets a bit complex.
            #
            # e.g. "backports.lru_cache". The "backports" namespace may temporarily point to
            #      another backports namespace directory, such as "backports/weakref/__init__.py"
            #      but "backports.lru_cache" isn't inside of that folder. It's actually in a
            #      completely separate directory. So we use :func:`filer.in_directory`
            #      to catch this edge case and return False.
            #
            return False

    return True


def _get_imported_namespaces_at_directories(directories):
    """Get every Pthon namespace dependency for every Python file in a set of folders.

    Args:
        directories (iter[str]):
            The absolute paths to folders on-disk that contain Python
            files. These Python files will be directly imported and
            parsed for either namespace imports and returned.

    Returns:
        set[:class:`python_compatibility.import_parser.Module`]:
            The dot-separated listing of every imported item.

    """
    namespaces = set()
    names = set()

    for directory in directories:
        for path in packaging.iter_python_files(directory):
            try:
                for namespace in import_parser.get_namespaces_from_file(path):
                    namespace_text = namespace.get_namespace()

                    if namespace_text not in names:
                        names.add(namespace_text)
                        namespaces.add(namespace)
            except SyntaxError:
                _LOGGER.exception('Could not load "%s" due to a syntax error', path)

    return namespaces


def _get_module_normal_namespace(namespace):
    try:
        return __import__(namespace)
    except ImportError:
        # Usually happens if the namespace is actually "foo.MyClass" or "foo.my_attribute"
        pass

    possible_module = imports.import_nearest_module(namespace)
    module_namespace = possible_module.__name__
    end_of_namespace = namespace[len(module_namespace) :].lstrip(".")

    if _module_has_attribute(possible_module, end_of_namespace):
        return possible_module

    return None


# TODO : Need unittests for this function
def _get_module_from_shared_namespace(namespace):
    # According to the documentation, to search within a namespace, you need to
    # have at least one "."
    #
    # Reference: https://docs.python.org/3/library/pkgutil.html#pkgutil.iter_importers
    #
    closest_module = _import_nearest_module_namespace(namespace)
    loader = pkgutil.find_loader(closest_module)

    if not loader:
        return None

    return _FakeModule(loader.get_filename())


def _get_nearest_module(namespace):
    """Find the module that most-closely represents the given namespace.

    Args:
        namespace (str):
            A Python dot-separated string such as "foo.bar.MyClass".
            This namespace may point to a module, class, or attribute.
            Basically, anything that's importable is valid input.

    Returns:
        module or NoneType: The found module, if any.

    """
    module = _get_module_normal_namespace(namespace)

    if module:
        return module

    return _get_module_from_shared_namespace(namespace)


def _get_source_paths(namespaces):
    """Find the paths on-disk to every given Python dot-separated string.

    Warning:
        If any namespace in `namespaces` is not importable for any
        reason, it will not be returned. In other words, not every
        namespace given is guaranteed to have an output.

    Args:
        namespaces (iter[str]):
            The dot-separated strings to check. e.g. "foo.bar.bazz".

    Returns:
        set[str]: The file paths on-disk where the namespaces point to.

    """
    paths = set()

    for namespace in namespaces:
        try:
            module = _get_nearest_module(namespace.get_namespace())
        except Exception:
            continue

        if not module:
            _LOGGER.error(
                'No parent module could be found for namespace "%s".', namespace
            )

            continue

        try:
            paths.add(os.path.realpath(module.__file__))
        except AttributeError:
            # This happens whenever `module` is a built-in, such as
            # :mod:`sys`. Just ignore this exception.
            #
            _LOGGER.warning('Module "%s" has no file path.', module)

            continue
        except Exception:
            _LOGGER.exception('Module "%s" could not be imported.', module)

            raise

    return paths


def _import_nearest_module_namespace(namespace):
    """Find the first shared namespace that correctly imports and return the namespace.

    Args:
        namespace (str): A dot-separated Python path.

    Returns:
        str: The namespace string (dot-separated Python path) to the first known module.

    """
    try:
        return __import__(namespace)
    except ImportError:
        # Usually happens if the namespace is actually "foo.MyClass" or "foo.my_attribute"
        pass

    while True:
        parts = namespace.split(".")
        parent = parts[:-1]

        if not parent:
            break

        new_namespace = ".".join(parent)

        try:
            __import__(new_namespace)
        except ImportError:
            # Usually happens if the namespace is actually "foo.MyClass" or "foo.my_attribute"
            pass
        else:
            return new_namespace

        namespace = new_namespace

    return ""


def _parse_arguments(text):
    """Get the user's chosen directories, parse them, and return them.

    Args:
        text (str): The raw user-provided text that was sent to the CLI.

    Returns:
        set[str]: The absolute paths on-disk to directories that will be queried.

    """
    parser = argparse.ArgumentParser(
        description="Find every Python module path that is imported from a list of directories"
    )

    parser.add_argument(
        "directories",
        nargs="+",
        default=set(),
        help="The root folders on-disk to some Python packages. Each path will be checked.",
    )

    directories = set()
    current_directory = os.getcwd()

    for path in set(parser.parse_args(text).directories):
        if not os.path.isabs(path):
            path = os.path.normpath(os.path.join(current_directory, path))

        directories.add(path)

    return directories


def get_dependency_paths(directories):
    """Find the dependencies of every Python file in `directories`.

    Args:
        directories (list[str]):
            The folders on-disk that may have Python files (with
            dependencies) to search through.

    Raises:
        NotImplementedError: If any path in `directories` doesn't exist.

    Returns:
        set[str]: The file paths on-disk where the namespaces point to.

    """
    missing = set()

    for directory in directories:
        if not os.path.isdir(directory):
            missing.add(directory)

    if missing:
        raise NotImplementedError(
            'Paths "{missing}" are not valid directories.'.format(missing=missing)
        )

    namespaces = _get_imported_namespaces_at_directories(directories)

    return _get_source_paths(namespaces)


def main(text):
    """Run the main execution of the current script.

    Note:
        This function set could support .egg files in the future but
        this hasn't been tested yet.

    Raises:
        NotImplementedError: If the user provides paths to don't point to directories.

    """
    directories = _parse_arguments(text)

    for path in sorted(get_dependency_paths(directories)):
        # These don't actually need to be sorted. But it makes debugging easier
        print(path)


if __name__ == "__main__":
    main(sys.argv[1:])
