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
        version=os.environ["REZ_BUILD_PROJECT_VERSION"],
        sub_path=sub_path,
    )

    return os.path.join(tar_directory, tar_name)


def _extract_all(path, destination):
    """Unpack `path` to the `destination` folder.

    Args:
        path (str): A tar file which will be unpacked.
        destination (str): A build folder used to put all of the extracted files.

    Returns:
        set[str]: All of the top-level files and folders of the unpacked tar file.

    """
    # Note: When using Python 3, use `shutil.unpack_archive`: https://stackoverflow.com/a/56182972
    with tarfile.open(path, "r:gz") as handler:
        members = handler.getmembers()
        handler.extractall(path=destination)

    return {
        os.path.join(destination, member.path)
        for member in members
        if os.sep not in member.path
    }


def _copy(paths, directory, overwrite=True):
    """Copy every file and folder from `paths` into `directory`.

    Args:
        paths (iter[str]): All files and folders which came from the unpacked tar.
        directory (str): The chosen install directory for the Rez package.
        overwrite (bool, optional): If True, delete files / folders before copying. Default is True.

    Raises:
        RuntimeError: If a destination file already exists but `overwrite` is not set to True.

    """
    for path in paths:
        destination = os.path.join(directory, os.path.basename(path))

        if os.path.isdir(path):
            if overwrite and os.path.isdir(destination):
                shutil.rmtree(destination)

            shutil.copytree(path, destination)
        elif os.path.isfile(path):
            if not overwrite and os.path.isfile(destination):
                raise RuntimeError(
                    'Cannot copy file. Path "{destination}" exists.'.format(
                        destination=destination
                    )
                )

            shutil.copy2(path, destination)


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
    _copy(paths, install)


if __name__ == "__main__":
    main(
        os.environ["REZ_BUILD_PATH"],
        os.environ["REZ_BUILD_INSTALL_PATH"],
    )
