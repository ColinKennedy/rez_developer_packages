#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Create helpful functions for building Rez packages, using Python."""

import collections
import contextlib
import functools
import glob
import io
import logging
import os
import shutil
import subprocess
import textwrap
import typing

import setuptools
import whichcraft

try:
    from rez.version import _requirement as requirement  # Rez 3.X+
except ImportError:
    from rez.vendor.version import requirement  # Rez 2.109-ish

from . import exceptions, linker, namespacer

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


def _find_api_documentation(entries: typing.Union[list[tuple[str, str]], str]) -> str:
    """Find the home page URL, given some entries.

    Args:
        entries:
            If a string is given, assume it's the home page and return
            it. Otherwise, search each key/value pair for a home page
            and return it, if found.

    Returns:
        The found home page URL, if any.

    """
    if isinstance(entries, str):
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


def _get_hotl_executable() -> str:
    """str: Find the path to a hotl executable, if any."""
    return os.path.normcase(whichcraft.which("hotl") or "")


def _get_python_requires() -> str:
    """str: Get the required Python version, if any."""
    for text in os.environ["REZ_USED_REQUEST"].split(" "):
        request = requirement.Requirement(text)

        if (
            request.name == "python"
            and not request.weak
            and "REZ_PYTHON_VERSION" in os.environ
        ):
            version = os.environ["REZ_PYTHON_VERSION"]

            return "=={version}".format(version=version)

    return ""


def _get_platform() -> str:
    """str: Get the required platform name, if any."""
    for text in os.environ["REZ_USED_REQUEST"].split(" "):
        request = requirement.Requirement(text)

        if request.name == "platform" and not request.weak:
            return str(request.range)

    return ""


def _iter_data_extensions(directory: str) -> typing.Generator[str, None, None]:
    """Get every non-Python extension within `directory`.

    Args:
        directory: Some absolute path to a directory on-disk.

    Yields:
        Each found extension, as a glob pattern. e.g. "*.txt".

    """
    for _, _, files in os.walk(directory):
        for path in files:
            _, extension = os.path.splitext(path)

            if extension not in _PYTHON_EXTENSIONS:
                yield "*" + extension


def _iter_python_modules(directory: str) -> typing.Generator[str, None, None]:
    """Find every child Python file (no extension) within `directory`."""
    for item in os.listdir(directory):
        base, extension = os.path.splitext(item)

        if extension in _PYTHON_EXTENSIONS:
            yield base


@contextlib.contextmanager
def _keep_cwd() -> typing.Generator[None, None, None]:
    """Save and store the user's current working directory."""
    original = os.getcwd()

    try:
        yield
    finally:
        os.chdir(original)


def _build_eggs(
    source: str,
    destination: str,
    name: str,
    setuptools_data: _SetuptoolsData,
    data_patterns: typing.Optional[list[str]] = None,
) -> None:
    """Create a .egg file for some Python directory.

    Args:
        source:
            The absolute path to the user's developer Rez package.
        destination:
            The absolute path to the installed Rez package path.
        name:
            The directory which contains Python modules which will be made into a .egg file.
        setuptools_data:
            The metadata which will be added to the .egg's EGG-INFO folder.
        data_patterns:
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
        package_data = {}

    python_modules = sorted(
        (
            os.path.splitext(path)[0]
            for path in _iter_python_modules(os.path.join(source, name))
        )
    )

    _LOGGER.debug('Found "%s" Python package data for the egg.', package_data)
    _LOGGER.debug('Found "%s" Python modules for the egg.', python_modules)

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


def _copy_file_or_folder(source: str, destination: str) -> None:
    """Copy ``source`` to ``destination`` regardless if it's a file, folder, etc.

    Args:
        source: An absolute path to a file, folder, etc.
        destination: The absolute path on-disk where ``source`` is copied to.

    """
    if os.path.isdir(source):
        _LOGGER.info('Copying "%s" folder.', source)
        shutil.copytree(source, destination, dirs_exist_ok=True)
    elif os.path.isfile(source):
        _LOGGER.info('Copying "%s" file.', source)
        shutil.copy2(source, destination)


def _make_shared_namespace(namespaces: list[str], root: str) -> str:
    """Recursively create shared namespaces for ``namespaces``, starting at ``root``.

    Args:
        namespaces: Each Python folder to create. e.g. ``["top", "other"]``.
        root: An absolute directory to begin a Python shared namespace.

    Returns:
        The inner-most sub-directory of ``namespaces``.

    """
    directories = [
        os.path.join(root, *namespaces[:index])
        for index in range(1, len(namespaces) + 1)
    ]

    parent = directories[-1]

    if not os.path.isdir(parent):
        os.makedirs(parent)

    for directory in directories:
        _make_shared_python_init(directory)

    return parent


def _make_shared_python_init(directory: str) -> None:
    """Register ``directory`` as a Python shared namespace.

    Args:
        directory: An absolute path on-disk to add a ``__init__.py`` file.

    """
    path = os.path.join(directory, "__init__.py")

    template = textwrap.dedent(
        """\
        import pkg_resources as __pkg_resources

        __pkg_resources.declare_namespace(__name__)
        """
    )

    with io.open(path, "w", encoding="ascii") as handler:
        handler.write(template)


def _run_command(  # pylint: disable=too-many-arguments,too-many-positional-arguments
    command: typing.Callable[[str, str], None],
    source: str,
    destination: str,
    symlink: bool = linker.must_symlink(),
    symlink_folders: bool = linker.must_symlink_folders(),
    symlink_files: bool = linker.must_symlink_files(),
) -> None:
    """Run a commany or symlink instead, depending on the given input.

    Args:
        command:
            Some function to run if it's determined to not do a symlink.
        source:
            Some absolute path to a file or folder on-disk.
        destination:
            The absolute path to where generated content will go.
        symlink:
            If True, symlinking will always happen. It implies
            If ``symlink_folders`` and ``symlink_files`` are both True.
            If False, symlinking is not guaranteed to always happen.
        symlink_folders:
            If True and ``source`` is a folder, make a symlink from
            ``destination`` which points back to ``source``. If False,
            run ``command`` instead.
        symlink_files:
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
        remove(destination)
        os.symlink(source, destination)
    else:
        _LOGGER.info('Running command "%s" on "%s".', command, destination)
        command(source, destination)


def _run_hotl(root: str, hda: str, symlink: bool = linker.must_symlink()) -> None:
    """Collapse or symlink Houdini HDA VCS folders.

    This function assumes that you're using expanded HDAs (HDAs which
    are folders, not single-files).

    Args:
        root:
            The absolute directory to folder where a houdini.hdalibrary file lives.
        hda:
            The absolute directory where the HDA will be built to.
        symlink:
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
    # Note: Remove the disable= once Python 2 support is dropped

    process = subprocess.Popen(  # pylint: disable=consider-using-with
        [executable, "-l", root, hda],
        stderr=subprocess.PIPE,
    )
    _, stderr = process.communicate()

    if process.returncode:
        _LOGGER.error('HDA "%s" failed to generate.', root)

        raise RuntimeError(stderr)


def _validate_egg_names(items: typing.Iterable[str]) -> None:
    """Check to ensure no item is in a sub-folder.

    Raises:
        NonRootItemFound: If ``items`` contains subfolder data.

    """
    invalids = set()

    for item in items:
        if "/" in item or "\\" in item:
            invalids.add(item)

    if invalids:
        raise exceptions.NonRootItemFound(
            'Found bad names "{invalids}".'.format(invalids=sorted(invalids))
        )


def build(  # pylint: disable=too-many-arguments,too-many-positional-arguments
    source: str,
    destination: str,
    hdas: typing.Iterable[str] = (),
    items: typing.Iterable[str] = (),
    eggs: typing.Iterable[str] = (),
    shared_python_packages: typing.Iterable[namespacer.PythonPackageItem] = (),
    symlink: bool = linker.must_symlink(),
    symlink_folders: bool = linker.must_symlink_folders(),
    symlink_files: bool = linker.must_symlink_files(),
) -> None:
    """Copy or symlink all items in ``source`` to ``destination``.

    Args:
        source:
            The absolute path to the root directory of the Rez package.
        destination:
            The location where the built files will be copied or symlinked from.
        hdas:
            The local paths to each folder containing HDAs. Default is None.
        items:
            The local paths to every item in `source` to copy / symlink. Default is None.
        eggs:
            The local paths which will be compressed into .egg (zip) files. Default is None.
        shared_python_packages:
            The local paths to every item in `source` to copy / symlink. Default is None.
        symlink:
            If True, symlinking will always happen. It implies
            If ``symlink_folders`` and ``symlink_files`` are both True.
            If False, symlinking is not guaranteed to always happen.
        symlink_folders:
            If True and ``source`` is a folder, make a symlink from
            ``destination`` which points back to ``source``. If False,
            run ``command`` instead.
        symlink_files:
            If True and ``source`` is a file, make a symlink from
            ``destination`` which points back to ``source``. If False,
            run ``command`` instead.

    """
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
                source,
                destination,
                hdas,
                symlink=symlink,
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

        if shared_python_packages:
            build_shared_python_packages(
                source,
                destination,
                shared_python_packages,
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


def build_eggs(  # pylint: disable=too-many-arguments,too-many-positional-arguments
    source: str,
    destination: str,
    eggs: typing.Iterable[str],
    symlink: bool = linker.must_symlink(),
    symlink_folders: bool = linker.must_symlink_folders(),
    symlink_files: bool = linker.must_symlink_files(),
    data_patterns: typing.Optional[list[str]] = None,
) -> None:
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
        data_patterns (list[str], optional):
            Any file extensions to include as data in the .egg. For
            example, if you have a .txt file within `source/name`, use
            `data_patterns=["*.txt"]` to include them in the .egg.
            Default is None.

    """
    _validate_egg_names(eggs)

    if not data_patterns:
        data_patterns = []

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
        description=os.getenv("REZ_BUILD_PROJECT_DESCRIPTION", ""),
        author=", ".join(package.authors or []),
        url=_find_api_documentation(package.help or []),
        python_requires=_get_python_requires(),
        platforms=platforms,
    )

    for name in eggs:
        source_path = os.path.join(source, name)
        destination_egg = os.path.join(destination, name + ".egg")

        _LOGGER.info(
            'Compiling "%s" Python source to "%s" egg destination.',
            source_path,
            destination_egg,
        )

        _run_command(
            functools.partial(
                _build_eggs,
                name=name,
                setuptools_data=setuptools_data,
                data_patterns=data_patterns,
            ),
            source_path,
            destination_egg,
            symlink,
            symlink_folders,
            symlink_files,
        )


def build_hdas(
    source: str,
    destination: str,
    hdas: typing.Iterable[str],
    symlink: bool = linker.must_symlink(),
) -> None:
    """Symlink or collapse VCS-style HDA folders to an installed Rez package.

    Args:
        source:
            The absolute path to the root directory of the Rez package.
        destination:
            The location where the built files will be copied or symlinked from.
        hdas:
            The name of each local folder which contains HDAs to build.
        symlink:
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

    if not os.path.isdir(destination):
        os.makedirs(destination)

    for library in sorted(libraries):
        hda_root = os.path.dirname(library)  # The root of the current HDA library
        library_root = os.path.dirname(hda_root)  # The folder containing all HDAs

        hda_destination = os.path.join(destination, os.path.basename(library_root))
        hda = os.path.join(hda_destination, os.path.basename(hda_root))

        _LOGGER.info(
            'Clearing and rebuilding "%s" HDA to "%s" destination',
            hda,
            hda_destination,
        )

        if os.path.isdir(hda_destination):
            shutil.rmtree(hda_destination)

        os.makedirs(hda_destination)

        _run_hotl(hda_root, hda, symlink=symlink)


def build_items(  # pylint: disable=too-many-arguments,too-many-positional-arguments
    source: str,
    destination: str,
    items: typing.Iterable[str],
    symlink: bool = linker.must_symlink(),
    symlink_folders: bool = linker.must_symlink_folders(),
    symlink_files: bool = linker.must_symlink_files(),
) -> None:
    """Copy or symlink all items in ``source`` to ``destination``.

    Args:
        source:
            The absolute path to the root directory of the Rez package.
        destination:
            The location where the built files will be copied or symlinked from.
        items:
            The local paths to every item in `source` to copy / symlink. Default is None.
        symlink:
            If True, symlinking will always happen. It implies
            If ``symlink_folders`` and ``symlink_files`` are both True.
            If False, symlinking is not guaranteed to always happen.
        symlink_folders:
            If True and ``source`` is a folder, make a symlink from
            ``destination`` which points back to ``source``. If False,
            run ``command`` instead.
        symlink_files:
            If True and ``source`` is a file, make a symlink from
            ``destination`` which points back to ``source``. If False,
            run ``command`` instead.

    """
    for item in items:
        source_path = os.path.join(source, item)
        destination_path = os.path.join(destination, item)

        _LOGGER.info(
            'Copying "%s" source to "%s" destination',
            source_path,
            destination_path,
        )

        _run_command(
            _copy_file_or_folder,
            source_path,
            destination_path,
            symlink,
            symlink_folders,
            symlink_files,
        )


def build_shared_python_packages(  # pylint: disable=too-many-arguments,too-many-positional-arguments
    source: str,
    destination: str,
    items: typing.Iterable[namespacer.PythonPackageItem],
    symlink: bool = linker.must_symlink(),
    symlink_folders: bool = linker.must_symlink_folders(),
    symlink_files: bool = linker.must_symlink_files(),
) -> None:
    """Copy or symlink all items in ``source`` to ``destination``.

    Args:
        source:
            The absolute path to the root directory of the Rez package.
        destination:
            The location where the built files will be copied or symlinked from.
        items:
            The local paths to every item in `source` to copy / symlink. Default is None.
        symlink:
            If True, symlinking will always happen. It implies
            If ``symlink_folders`` and ``symlink_files`` are both True.
            If False, symlinking is not guaranteed to always happen.
        symlink_folders:
            If True and ``source`` is a folder, make a symlink from
            ``destination`` which points back to ``source``. If False,
            run ``command`` instead.
        symlink_files:
            If True and ``source`` is a file, make a symlink from
            ``destination`` which points back to ``source``. If False,
            run ``command`` instead.

    """
    for entry in items:
        namespace = entry.namespace_parts
        name = entry.relative_path

        source_path = os.path.join(source, name)
        destination_path = os.path.join(destination, name)

        if namespace:
            destination_path = _make_shared_namespace(namespace, destination_path)

        _LOGGER.info(
            'Copying Python package "%s" source to "%s" destination',
            source_path,
            destination_path,
        )

        _run_command(
            _copy_file_or_folder,
            source_path,
            destination_path,
            symlink,
            symlink_folders,
            symlink_files,
        )


def clean(path: str) -> None:
    """Delete and re-make the ``path`` folder."""
    _LOGGER.info('Deleting "%s" path and remaking it.', path)

    remove(path)  # Clean any old build folder
    os.makedirs(path)


def remove(path: str) -> None:
    """Delete whatever `path` is.

    Args:
        path: A directory or file or symlink.

    """
    if os.path.islink(path) or os.path.isfile(path):
        os.remove(path)
    elif os.path.isdir(path):
        shutil.rmtree(path)
