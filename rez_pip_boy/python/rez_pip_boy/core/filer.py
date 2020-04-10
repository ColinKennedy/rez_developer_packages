#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Generic "file path" specific funcions."""

import os
import tarfile

from rez_utilities import inspection

# TODO : Remove this later. It's just for testing
os.environ["REZ_PIP_BOY_TAR_LOCATION"] = "/tmp/some/spot"

_ROOT = os.environ["REZ_PIP_BOY_TAR_LOCATION"]


def _get_transfer_path(variant):
    """Get the recommended file path to the archived .tar.gz file.

    Args:
        variant (:class:`rez.packages.Variant`):
            The specification of a Rez package which will be archived
            and later unpacked.

    Returns:
        str: The generated path to the .tar.gz.

    """
    subpath = (
        variant._non_shortlinked_subpath.replace("/", "_")
        .replace("\\", "_")
        .replace(" ", "_")
    )
    tar_name = "{variant.name}-{variant.version}-{subpath}.tar.gz".format(
        variant=variant, subpath=subpath,
    )

    return os.path.join(_ROOT, variant.name, tar_name)


def transfer(variant):
    """Archive a Rez variant into a .tar.gz file.

    The .tar.gz file later is used to unpack and install the Rez package.

    Args:
        variant (:class:`rez.packages.Variant`):
            The specification of a Rez package which will be archived
            and later unpacked.

    """
    source_root = inspection.get_package_root(variant)

    # TODO : Double-check that this works with non-hashed variants
    source = os.path.join(
        source_root,
        variant._non_shortlinked_subpath,  # pylint: disable=protected-access
    )
    destination = _get_transfer_path(variant)
    destination_directory = os.path.dirname(destination)

    if not os.path.isdir(destination_directory):
        os.makedirs(destination_directory)

    with tarfile.open(destination, "w:gz") as handler:
        for item in os.listdir(source):
            handler.add(os.path.join(source, item), arcname=item)
