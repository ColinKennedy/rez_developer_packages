#!/usr/bin/env python
# -*- coding: utf-8 -*-

import shutil
import os


def main(source, install):
    """Run the main execution of the current script."""
    files = [
        (os.path.join(source, "src", "rpm2cpio.py"), os.path.join(install, "python", "rpm2cpio.py")),
    ]

    if os.path.isdir(install):
        shutil.rmtree(install)

    for old, new in files:
        directory = os.path.dirname(new)

        if not os.path.isdir(directory):
            os.makedirs(directory)

        shutil.copy2(old, new)


if __name__ == "__main__":
    main(os.environ["REZ_BUILD_SOURCE_PATH"], os.environ["REZ_BUILD_INSTALL_PATH"])
