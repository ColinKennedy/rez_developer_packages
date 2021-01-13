#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Create helpful functions for building Rez packages, using Python."""

import collections
import contextlib
import functools
import glob
import logging
import os
import shutil
import subprocess

import setuptools
import six
import whichcraft
from rez.vendor.version import requirement

from . import exceptions, linker

try:
    from rez import packages  # Newer Rez versions, 2.51+-ish
except ImportError:
    from rez import packages_ as packages  # Older Rez versions. 2.48-ish


_SetuptoolsData = collections.namedtuple(
    "_SetuptoolsData",
    "package_name, version, description, author, url, python_requires, platforms",
)
_LOGGER = logging.getLogger(__name__)
_PYTHON_EXTENSIONS = frozenset((".py", ".pyc", ".pyd"))


def _find_api_documentation(entries):
    """Find the home page URL, given some entries.

    Args:
        entries (list[str] or str):
            If a string is given, assume it's the home page and return
            it. Otherwise, search each key/value pair for a home page
            and return it, if found.

    Returns:
        str: The found home page URL, if any.

    """
    if isinstance(entries, six.string_types):
        return entries

    for token in ("Home Page", "Source Code"):
        for key, value in entries or []:
            # Reference: https://github.com/nerdvegas/rez/blob/b21516589933afeed1e1a1a439962d2e20151e2d/src/rez/pip.py#L443-L447  pylint: disable=line-too-long
            if key == token:
                return value

    for token in ("api", "documentation", "docs"):
        for key, value in entries or []:
            if token in key.lower():
                return value

    return ""


def _get_hotl_executable():
    """str: Find the path to a hotl executable, if any."""
    return whichcraft.which("hotl") or ""


def _get_python_requires():
    """str: Get the required Python version, if any."""
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
    """str: Get the required platform name, if any."""
    for text in os.environ["REZ_USED_REQUEST"].split(" "):
        request = requirement.Requirement(text)

        if request.name == "platform" and not request.weak:
            return str(request.range)

    return ""


def _iter_data_extensions(directory):
    """Get every non-Python extension within `directory`.

    Args:
        directory (str): Some absolute path to a directory on-disk.

    Yields:
        str: Each found extension, as a glob pattern. e.g. "*.txt".

    """
    for _, _, files in os.walk(directory):
        for path in files:
            _, extension = os.path.splitext(path)

            if extension not in _PYTHON_EXTENSIONS:
                yield "*" + extension


def _iter_python_modules(directory):
    """str: Find  very child Python file (no extension) within `directory`."""
    for item in os.listdir(directory):
        base, extension = os.path.splitext(item)

        if extension in _PYTHON_EXTENSIONS:
            yield base


@contextlib.contextmanager
def _keep_cwd():
    """Save and store the user's current working directory."""
    original = os.getcwd()

    try:
        yield
    finally:
        os.chdir(original)


def _build_eggs(source, destination, name, setuptools_data, data_patterns=None):
    """Create a .egg file for some Python directory.

    Args:
        source (str):
            The absolute path to the user's developer Rez package.
        destination (str):
            The absolute path to the installed Rez package path.
        name (str):
            The directory which contains Python modules which will be made into a .egg file.
        setuptools_data (:attr:`._SetuptoolsData`):
            The metadata which will be added to the .egg's EGG-INFO folder.
        data_patterns (list[str], optional):
            Any file extensions to include as data in the .egg. For
            example, if you have a .txt file within `source/name`, use
            `data_patterns=["*.txt"]` to include them in the .egg.
            Default is None.

    """
    source = os.path.dirname(source)
    destination = os.path.dirname(destination)

    if not data_patterns:
        data_patterns = sorted(set(_iter_data_extensions(os.path.join(source, name))))

    if data_patterns:
        package_data = {"": data_patterns}
    else:
        package_data = dict()

    python_modules = sorted(
        (
            os.path.splitext(path)[0]
            for path in _iter_python_modules(os.path.join(source, name))
        )
    )

    with _keep_cwd():
        os.chdir(source)

        setuptools.setup(
            name=setuptools_data.package_name,
            version=setuptools_data.version,
            description=setuptools_data.description,
            author=setuptools_data.author,
            url=setuptools_data.url,
            package_data=package_data,  # Reference: https://setuptools.readthedocs.io/en/latest/userguide/datafiles.html  pylint: disable=line-too-long
            # For `convert_2to3_doctests`. I shouldn't need to add
            # this but tests will fail without it, on setuptools-44.
            #
            convert_2to3_doctests=[],
            packages=setuptools.find_packages(name),
            package_dir={"": name},
            platforms=setuptools_data.platforms,
            py_modules=python_modules,
            include_package_data=True,  # Reference: https://python-packaging.readthedocs.io/en/latest/non-code-files.html  pylint: disable=line-too-long
            python_requires=setuptools_data.python_requires,
            script_args=["bdist_egg"],  # Reference: https://stackoverflow.com/a/2851036
        )

        distribution_directory = os.path.join(os.getcwd(), "dist")
        egg_directory = os.path.join(distribution_directory, "*.egg")
        egg = list(glob.glob(egg_directory))[0]

        destination_path = os.path.join(destination, name + ".egg")
        shutil.copy2(egg, destination_path)


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


def _run_hotl(root, hda, symlink=linker.must_symlink()):
    """Collapse or symlink Houdini HDA VCS folders.

    This function assumes that you're using expanded HDAs (HDAs which
    are folders, not single-files).

    Args:
        root (str):
            The absolute directory to folder where a houdini.hdalibrary file lives.
        hda (str):
            The absolute directory where the HDA will be built to.
        symlink (bool, optional):
            If True, symlink ``root`` to ``hda``. If False, collapse the
            HDA in ``root`` into a single file and copy it into ``hda``.

    Raises:
        EnvironmentError: If no ``hotl`` executable could be found.
        RuntimeError: If calling ``hotl`` errored, for any reason.

    """
    executable = _get_hotl_executable()

    if not os.path.isfile(executable):
        raise EnvironmentError(
            'Path "{executable}" is not an executable file. '
            "Make sure you have Houdini included in your package requirements.".format(
                executable=executable
            )
        )

    if symlink:
        _LOGGER.info('Creating symlink "%s" -> "%s".', root, hda)
        os.symlink(root, hda)

        return

    _LOGGER.info('Collapsing "%s" HDA to "%s".', root, hda)
    process = subprocess.Popen([executable, "-l", root, hda], stderr=subprocess.PIPE)
    _, stderr = process.communicate()

    if stderr:
        _LOGGER.error('HDA "%s" failed to generate.', root)

        raise RuntimeError(stderr)


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
    hdas=None,
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
        hdas (iter[str], optional):
            The local paths to each folder containing HDAs. Default is None.
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
    if not hdas:
        hdas = []

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

        if hdas:
            build_hdas(
                source, destination, hdas, symlink=symlink,
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
    except (EnvironmentError, RuntimeError):
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
    data_patterns=None,
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

    if not data_patterns:
        data_patterns = set()

    package = packages.get_developer_package(
        os.path.dirname(os.environ["REZ_BUILD_PROJECT_FILE"])
    )
    platform = _get_platform()

    if platform:
        platforms = [platform]
    else:
        # This is apparently a common value to many "Linux, Windows, etc"
        platforms = ["any"]

    setuptools_data = _SetuptoolsData(
        package_name=os.environ["REZ_BUILD_PROJECT_NAME"],
        version=os.environ["REZ_BUILD_PROJECT_VERSION"],
        description=os.environ["REZ_BUILD_PROJECT_DESCRIPTION"],
        author=", ".join(package.authors or []),
        url=_find_api_documentation(package.help or []),
        python_requires=_get_python_requires(),
        platforms=platforms,
    )

    for name in eggs:
        _run_command(
            functools.partial(
                _build_eggs,
                name=name,
                setuptools_data=setuptools_data,
                data_patterns=data_patterns,
            ),
            os.path.join(source, name),
            os.path.join(destination, name + ".egg"),
            symlink,
            symlink_folders,
            symlink_files,
        )


def build_hdas(
    source, destination, hdas, symlink=linker.must_symlink(),
):
    """Symlink or collapse VCS-style HDA folders to an installed Rez package.

    Args:
        source (str):
            The absolute path to the root directory of the Rez package.
        destination (str):
            The location where the built files will be copied or symlinked from.
        hdas (iter[str]):
            The name of each local folder which contains HDAs to build.
        symlink (bool, optional):
            If True, symlinking will always happen. It implies
            If ``symlink_folders`` and ``symlink_files`` are both True.
            If False, symlinking is not guaranteed to always happen.

    Raises:
        RuntimeError:
            If any name in ``hdas`` is not a folder on-disk or a folder
            which does not contain HDA definitions.

    """
    libraries = set()

    for folder_name in hdas:
        location = os.path.join(source, folder_name, "*", "houdini.hdalibrary")
        folder_libraries = list(glob.glob(location))

        if not folder_libraries:
            raise RuntimeError(
                'Directory "{location}" has no VCS-style HDAs inside of it.'.format(
                    location=location
                )
            )

        libraries.update(folder_libraries)

    libraries = sorted(libraries)

    if not os.path.isdir(destination):
        os.makedirs(destination)

    for library in libraries:
        hda_root = os.path.dirname(library)  # The root of the current HDA library
        library_root = os.path.dirname(hda_root)  # The folder containing all HDAs

        hda_destination = os.path.join(destination, os.path.basename(library_root),)

        if os.path.isdir(hda_destination):
            shutil.rmtree(hda_destination)

        os.makedirs(hda_destination)

        hda = os.path.join(hda_destination, os.path.basename(hda_root))

        _run_hotl(hda_root, hda, symlink=symlink)


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
