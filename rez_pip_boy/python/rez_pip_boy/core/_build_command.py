#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""A module responsible for building the current Rez package."""

import os
import shutil
import tarfile


def _get_tar_path():
    """Find the path on-disk where an installed Rez variant package lives.

    This file is **not** the same kind of tar.gz file you might install
    from a Rez package from pypi.org. It's the **results** of a rez-pip
    install. e.g. this variant is for a specific Rez package variant. It
    needs to match the user's variant, exactly.

    Returns:
        str: The absolute path to where the expected tar file lives.

    """
    package_name = os.environ["REZ_BUILD_PROJECT_NAME"]

    tar_directory = os.path.join(
        os.environ["PIP_BOY_TAR_LOCATION"],
        package_name,
    )
    sub_path = convert_variant_sub_path(os.environ["REZ_BUILD_VARIANT_SUBPATH"])

    tar_name = "{package_name}-{version}-{sub_path}.tar.gz".format(
        package_name=package_name,
        version=_get_expected_tar_version(),
        sub_path=sub_path,
    )

    return os.path.join(tar_directory, tar_name)


def _get_expected_tar_version():
    """Find the most appropriate version to set for the current package.

    Sometimes a Rez package version differs from the expected version where we
    need to search for a .tar.gz. For example if you make a package but then
    realize later that you need to patch the package because something was
    wrong. The Rez version may be 1.2.3-1, to indicate a ``-1`` patch. But the
    real Python version might actually be 1.2.3.

    If no version was found, it's expected that Rez should provide a fallback
    version to use.

    Note:
        This function needs tests.

    Returns:
        str: The version needed to search for a .tar.gz file.

    """
    version = os.getenv("REZ_PIP_BOY_PROJECT_VERSION")

    if version:
        return version

    return os.environ["REZ_BUILD_PROJECT_VERSION"]


def _extract_all(path, destination):
    """Unpack `path` to the `destination` folder.

    Args:
        path (str): A tar file which will be unpacked.
        destination (str): A build folder used to put all of the extracted files.

    Returns:
        set[str]: All of the top-level files and folders of the unpacked tar file.

    """
    if hasattr(shutil, "unpack_archive"):
        # Note: Python 3+
        shutil.unpack_archive(path, destination)

        return [os.path.join(destination, item) for item in os.listdir(destination)]

    with tarfile.open(path, "r:gz") as handler:
        members = handler.getmembers()
        handler.extractall(path=destination)

    return {
        os.path.join(destination, member.path)
        for member in members
        if os.sep not in member.path
    }


def _copy(paths, directory):
    """Copy every file and folder from `paths` into `directory`.

    Args:
        paths (iter[str]): All files and folders which came from the unpacked tar.
        directory (str): The chosen install directory for the Rez package.

    """
    for path in paths:
        destination = os.path.join(directory, os.path.basename(path))

        if os.path.isdir(path):
            shutil.copytree(path, destination)
        elif os.path.isfile(path):
            shutil.copy2(path, destination)


def _delete_children(directory):
    """Clear the contents of ``directory`` without deleting ``directory``, itself.

    Args:
        directory (str): An absolute path to a directory on-disk.

    """
    if not os.path.isdir(directory):
        return

    for item in os.listdir(directory):
        full = os.path.join(directory, item)

        if os.path.isfile(full):
            os.remove(full)
        elif os.path.isdir(full):
            shutil.rmtree(full)
        elif os.path.islink(full):
            os.remove(full)


def convert_variant_sub_path(text):
    """str: Convert `text` which may contain file-path characters into a file path."""
    return text.replace("/", "_").replace("\\", "_").replace(" ", "_")


# Note: pylint's disable=missing-raises-doc is bugged. Add it back in once it's fixed
def main(build, install):  # pylint: disable=missing-raises-doc
    """Unpack a tar archive of some pip package and install it as a Rez package.

    Args:
        build (str):
            A temporary location to assemble the extracted files.
        install (str):
            The final folder where all unpacked files and folders will go.

    Raises:
        EnvironmentError:
            If the current Rez package + variant has no tar file to read from.

    """
    tar_path = _get_tar_path()

    if not os.path.isfile(tar_path):
        raise EnvironmentError(
            'Cannot install package. "{tar_path}" is missing.'.format(tar_path=tar_path)
        )

    paths = _extract_all(tar_path, build)
    _delete_children(install)
    _copy(paths, install)


if __name__ == "__main__":
    main(
        os.environ["REZ_BUILD_PATH"],
        os.environ["REZ_BUILD_INSTALL_PATH"],
    )
