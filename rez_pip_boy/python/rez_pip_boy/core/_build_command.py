#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import shutil
import tarfile

# TODO : Remove this later
os.environ["REZ_PIP_BOY_TAR_LOCATION"] = "/tmp/some/spot"


def _get_tar_path():
    package_name = os.environ["REZ_BUILD_PROJECT_NAME"]

    tar_directory = os.path.join(
        os.environ["REZ_PIP_BOY_TAR_LOCATION"],
        package_name,
    )

    tar_name = "{package_name}-{version}-{variant}.tar.gz".format(
        package_name=package_name,
        version=os.environ["REZ_BUILD_PROJECT_VERSION"],
        variant=os.environ["REZ_BUILD_VARIANT_SUBPATH"],
    )

    return os.path.join(tar_directory, tar_name)


def _extract_all(path, destination):
    # Note: When using Python 3, use `shutil.unpack_archive`: https://stackoverflow.com/a/56182972
    with tarfile.open(path, "r:gz") as handler:
        members = handler.getmembers()
        handler.extractall(path=destination)

    return {os.path.join(destination, member.path) for member in members if os.sep not in member.path}


def _copy(paths, directory):
    for path in paths:
        destination = os.path.join(directory, os.path.basename(path))

        if os.path.isdir(path):
            shutil.copytree(path, destination)
        elif os.path.isfile(path):
            shutil.copy2(path, destination)


def main(source, build, install):
    tar_path = _get_tar_path()

    if not os.path.isfile(tar_path):
        raise EnvironmentError(
            'Cannot install package. "{tar_path}" is missing.'.format(tar_path=tar_path)
        )

    paths = _extract_all(tar_path, build)
    _copy(paths, install)


if __name__ == "__main__":
    main(
        os.environ["REZ_BUILD_SOURCE_PATH"],
        os.environ["REZ_BUILD_PATH"],
        os.environ["REZ_BUILD_INSTALL_PATH"],
    )
