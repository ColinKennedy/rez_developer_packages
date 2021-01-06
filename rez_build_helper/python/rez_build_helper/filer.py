#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Create helpful functions for building Rez packages, using Python."""

import atexit
import functools
import contextlib
import glob
import logging
import os
import shutil

import setuptools
from rez.vendor.version import requirement
try:
    from rez import packages  # Newer Rez versions, 2.51+-ish
except ImportError:
    from rez import packages_ as packages  # Older Rez versions. 2.48-ish
import six

from . import exceptions, linker


_LOGGER = logging.getLogger(__name__)


def _find_api_documentation(entries):
    if isinstance(entries, six.string_types):
        return entries

    for key, value in entries or []:
        if "api" in key.lower():
            return value

    for key, value in entries or []:
        if "documentation" in key.lower():
            return value

    for key, value in entries or []:
        if "docs" in key.lower():
            return value

    for key, value in entries or []:
        # Reference: https://github.com/nerdvegas/rez/blob/b21516589933afeed1e1a1a439962d2e20151e2d/src/rez/pip.py#L443-L447
        if key == "Home Page":
            return value

    for key, value in entries or []:
        # Reference: https://github.com/nerdvegas/rez/blob/b21516589933afeed1e1a1a439962d2e20151e2d/src/rez/pip.py#L443-L447
        if key == "Source Code":
            return value

    return ""


def _get_python_requires():
    for text in os.environ["REZ_USED_REQUEST"].split(" "):
        request = requirement.Requirement(text)

        if request.name == "python" and not request.weak:
            # rez/utils/py_dist.py has convert_version, which apparently
            # shows that any Rez version syntax will work with dist. So
            # we'll do the same.
            #
            return str(request.range)

    return ""


def _get_platform():
    for text in os.environ["REZ_USED_REQUEST"].split(" "):
        request = requirement.Requirement(text)

        if request.name == "platform" and not request.weak:
            return str(request.range)

    return ""


@contextlib.contextmanager
def _keep_cwd():
    original = os.getcwd()

    try:
        yield
    finally:
        os.chdir(original)


def _run_command(  # pylint: disable=too-many-arguments
    command, source, destination, symlink, symlink_folders, symlink_files,
):
    """Run a commany or symlink instead, depending on the given input.

    Args:
        command (callable[str, str]):
            Some function to run if it's determined to not do a symlink.
        source (str):
            Some absolute path to a file or folder on-disk.
        destination (str):
            The absolute path to where generated content will go.
        symlink (bool):
            If True, symlinking will always happen. It implies
            If ``symlink_folders`` and ``symlink_files`` are both True.
            If False, symlinking is not guaranteed to always happen.
        symlink_folders (bool):
            If True and ``source`` is a folder, make a symlink from
            ``destination`` which points back to ``source``. If False,
            run ``command`` instead.
        symlink_files (bool):
            If True and ``source`` is a file, make a symlink from
            ``destination`` which points back to ``source``. If False,
            run ``command`` instead.

    Raises:
        RuntimeError: If ``source`` does not exist.

    """
    if not os.path.exists(source):
        raise RuntimeError(
            'Path "{source}" does not exist. Cannot continue.'.format(source=source)
        )

    if (
        symlink
        or (symlink_folders and os.path.isdir(source))
        or (symlink_files and os.path.isfile(source))
    ):
        _LOGGER.info('Creating "%s" symlink.', destination)
        os.symlink(source, destination)
    else:
        _LOGGER.info('Running command on "%s".', destination)
        command(source, destination)


def _validate_egg_names(items):
    """Check to ensure no item is in a sub-folder."""
    invalids = set()

    for item in items:
        if "/" in item or "\\" in item:
            invalids.add(item)

    if invalids:
        raise exceptions.NonRootItemFound(
            'Found bad names "{invalids}".'.format(invalids=sorted(invalids))
        )


def build(  # pylint: disable=too-many-arguments
    source,
    destination,
    items=None,
    eggs=None,
    symlink=linker.must_symlink(),
    symlink_folders=linker.must_symlink_folders(),
    symlink_files=linker.must_symlink_files(),
):
    """Copy or symlink all items in ``source`` to ``destination``.

    Args:
        source (str):
            The absolute path to the root directory of the Rez package.
        destination (str):
            The location where the built files will be copied or symlinked from.
        items (iter[str], optional):
            The local paths to every item in `source` to copy / symlink. Default is None.
        eggs (iter[str], optional):
            The local paths which will be compressed into .egg (zip) files. Default is None.
        symlink (bool, optional):
            If True, symlinking will always happen. It implies
            If ``symlink_folders`` and ``symlink_files`` are both True.
            If False, symlinking is not guaranteed to always happen.
        symlink_folders (bool, optional):
            If True and ``source`` is a folder, make a symlink from
            ``destination`` which points back to ``source``. If False,
            run ``command`` instead.
        symlink_files (bool, optional):
            If True and ``source`` is a file, make a symlink from
            ``destination`` which points back to ``source``. If False,
            run ``command`` instead.

    """
    if not items:
        items = []

    if not eggs:
        eggs = []

    try:
        if eggs:
            build_eggs(
                source,
                destination,
                eggs,
                symlink=symlink,
                symlink_folders=symlink_folders,
                symlink_files=symlink_files,
            )

        if items:
            build_items(
                source,
                destination,
                items,
                symlink=symlink,
                symlink_folders=symlink_folders,
                symlink_files=symlink_files,
            )
    except RuntimeError:
        # If the build errors early for any reason, delete the
        # destination folder. This is done to prevent a situation where
        # we have a "partial install".
        #
        shutil.rmtree(destination)

        raise


def build_eggs(  # pylint: disable=too-many-arguments
    source,
    destination,
    eggs,
    symlink=linker.must_symlink(),
    symlink_folders=linker.must_symlink_folders(),
    symlink_files=linker.must_symlink_files(),
):
    """Copy or symlink all items in ``source`` to ``destination``.

    Args:
        source (str):
            The absolute path to the root directory of the Rez package.
        destination (str):
            The location where the built files will be copied or symlinked from.
        eggs (iter[str], optional):
            The local paths which will be compressed into .egg (zip) files. Default is None.
        symlink (bool, optional):
            If True, symlinking will always happen. It implies
            If ``symlink_folders`` and ``symlink_files`` are both True.
            If False, symlinking is not guaranteed to always happen.
        symlink_folders (bool, optional):
            If True and ``source`` is a folder, make a symlink from
            ``destination`` which points back to ``source``. If False,
            run ``command`` instead.
        symlink_files (bool, optional):
            If True and ``source`` is a file, make a symlink from
            ``destination`` which points back to ``source``. If False,
            run ``command`` instead.

    """
    _validate_egg_names(eggs)

    package_name = os.environ["REZ_BUILD_PROJECT_NAME"]
    version = os.environ["REZ_BUILD_PROJECT_VERSION"]
    description = os.environ["REZ_BUILD_PROJECT_DESCRIPTION"]
    package = packages.get_developer_package(os.path.dirname(os.environ["REZ_BUILD_PROJECT_FILE"]))
    author = ", ".join(package.authors or [])
    url = _find_api_documentation(package.help or [])
    python_requires = _get_python_requires()
    platform = _get_platform()

    if platform:
        platforms = [_get_platform()]
    else:
        platforms = ["any"]  # This is apparently a common value to many "Linux, Windows, etc"

    for name in eggs:
        with _keep_cwd():
            os.chdir(source)

            setuptools.setup(
                name=package_name,
                version=version,
                description=description,
                author=author,
                url=url,
                packages=setuptools.find_packages(name),
                package_dir={"": name},
                platforms=platforms,
                py_modules=[
                    os.path.splitext(os.path.basename(path))[0]
                    for path in glob.glob(os.path.join(source, name, "*.py"))
                ],
                include_package_data=True,  # Reference: https://python-packaging.readthedocs.io/en/latest/non-code-files.html
                python_requires=python_requires,
                script="setup.py",  # Reference: https://stackoverflow.com/a/2851036
                script_args=["bdist_egg"],  # Reference: https://stackoverflow.com/a/2851036
            )

            distribution_directory = os.path.join(os.getcwd(), "dist")
            egg_directory = os.path.join(distribution_directory, "*.egg")
            egg = list(glob.glob(egg_directory))[0]

            destination_path = os.path.join(destination, name + ".egg")
            shutil.copy2(egg, destination_path)


def build_items(  # pylint: disable=too-many-arguments
    source,
    destination,
    items,
    symlink=linker.must_symlink(),
    symlink_folders=linker.must_symlink_folders(),
    symlink_files=linker.must_symlink_files(),
):
    """Copy or symlink all items in ``source`` to ``destination``.

    Args:
        source (str):
            The absolute path to the root directory of the Rez package.
        destination (str):
            The location where the built files will be copied or symlinked from.
        items (iter[str], optional):
            The local paths to every item in `source` to copy / symlink. Default is None.
        symlink (bool, optional):
            If True, symlinking will always happen. It implies
            If ``symlink_folders`` and ``symlink_files`` are both True.
            If False, symlinking is not guaranteed to always happen.
        symlink_folders (bool, optional):
            If True and ``source`` is a folder, make a symlink from
            ``destination`` which points back to ``source``. If False,
            run ``command`` instead.
        symlink_files (bool, optional):
            If True and ``source`` is a file, make a symlink from
            ``destination`` which points back to ``source``. If False,
            run ``command`` instead.

    """

    def _copy_file_or_folder(source, destination):
        if os.path.isdir(source):
            _LOGGER.info('Copying "%s" folder.', source)
            shutil.copytree(source, destination)
        elif os.path.isfile(source):
            _LOGGER.info('Copying "%s" file.', source)
            shutil.copy2(source, destination)

    for item in items:
        source_path = os.path.join(source, item)
        destination_path = os.path.join(destination, item)

        _run_command(
            _copy_file_or_folder,
            source_path,
            destination_path,
            symlink,
            symlink_folders,
            symlink_files,
        )


def clean(path):
    """Delete and re-make the ``path`` folder."""
    remove(path)  # Clean any old build folder
    os.makedirs(path)


def remove(path):
    """Delete whatever `path` is.

    Args:
        path (str): A directory or file or symlink.

    """
    if os.path.islink(path) or os.path.isfile(path):
        os.remove(path)
    elif os.path.isdir(path):
        shutil.rmtree(path)
