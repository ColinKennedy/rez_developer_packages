#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import shutil

from rez_utilities import inspection


def transfer(source, destination):
    package = inspection.get_nearest_rez_package(source)
    root = inspection.get_packages_path_from_package(package)
    relative_destination_path = os.path.relpath(source, root)

    shutil.copytree(source, os.path.join(destination, relative_destination_path))
