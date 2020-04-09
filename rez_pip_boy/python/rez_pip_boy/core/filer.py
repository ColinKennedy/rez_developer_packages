#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import tarfile

from rez_utilities import inspection


# TODO : Remove this later. It's just for testing
os.environ["REZ_PIP_BOY_TAR_LOCATION"] = "/tmp/some/spot"

_ROOT = os.environ["REZ_PIP_BOY_TAR_LOCATION"]


def _get_transfer_path(variant):
    tar_name = "{variant.name}-{variant.version}-{variant._non_shortlinked_subpath}.tar.gz".format(
        variant=variant)

    return os.path.join(_ROOT, variant.name, tar_name)


def transfer(variant):
    source_root = inspection.get_package_root(variant)

    # TODO : Double-check that this works with non-hashed variants
    source = os.path.join(source_root, variant._non_shortlinked_subpath)
    destination = _get_transfer_path(variant)
    destination_directory = os.path.dirname(destination)

    if not os.path.isdir(destination_directory):
        os.makedirs(destination_directory)

    with tarfile.open(destination, "w:gz") as handler:
        for item in os.listdir(source):
            handler.add(os.path.join(source, item), arcname=item)
