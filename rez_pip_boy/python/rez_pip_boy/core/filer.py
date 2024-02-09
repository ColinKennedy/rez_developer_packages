#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Generic "file path" specific funcions."""

import os
import tarfile

from rez_utilities import finder

from . import _build_command


def _get_transfer_path(root, variant):
    """Get the recommended file path to the archived .tar.gz file.

    Args:
        root (str):
            An absolute path to the top-level directory where tars will be copied to.
            Usually this is just ``$PIP_BOY_TAR_LOCATION``.
        variant (rez.packages.Variant):
            The specification of a Rez package which will be archived
            and later unpacked.

    Returns:
        str: The generated path to the .tar.gz.

    """
    sub_path = _build_command.convert_variant_sub_path(
        variant._non_shortlinked_subpath,  # pylint: disable=protected-access
    )
    tar_name = "{variant.name}-{variant.version}-{sub_path}.tar.gz".format(
        variant=variant,
        sub_path=sub_path,
    )

    return os.path.join(root, variant.name, tar_name)


def transfer(root, variant):
    """Archive a Rez variant into a .tar.gz file.

    The .tar.gz file later is used to unpack and install the Rez package.

    Args:
        root (str):
            An absolute path to the top-level directory where tars will be copied to.
            Usually this is just ``$PIP_BOY_TAR_LOCATION``.
        variant (rez.packages.Variant):
            The specification of a Rez package which will be archived
            and later unpacked.

    """
    source_root = finder.get_package_root(variant)

    source = os.path.join(
        source_root,
        variant._non_shortlinked_subpath,  # pylint: disable=protected-access
    )
    destination = _get_transfer_path(root, variant)
    destination_directory = os.path.dirname(destination)

    if not os.path.isdir(destination_directory):  # pragma: no cover
        os.makedirs(destination_directory)

    with tarfile.open(destination, "w:gz") as handler:
        for item in os.listdir(source):
            handler.add(os.path.join(source, item), arcname=item)
