#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""A set of basic classes and functions to make unittesting for ``rez_lint`` a bit easier."""

import os
import tempfile
import textwrap
import unittest

from python_compatibility.testing import common
from rez import packages_
from rez_utilities import creator, inspection


def _make_fake_source_package(name, text):
    """Create a Rez source package using the given `name`.

    Args:
        name (str): The name of the source Rez packge to create.
        text (str): The text that will be used for a "package.py" file.

    Returns:
        str: The directory on-disk that points to the root of the Rez package.

    """
    directory = os.path.join(tempfile.mkdtemp("_some_rez_source_package"), name)
    os.makedirs(directory)

    with open(os.path.join(directory, "package.py"), "w") as handler:
        handler.write(text)

    return directory


class BasePackaging(common.Common):
    """A simple class for testing in ``rez_lint``. Its job is to make Rez installed packages."""

    def _make_installed_package(self, name, text):
        """Create a Rez source package and install it into a temporary directory.

        All temporary directories will be marked for clean-up. Clean-up
        occurs after each test is run.

        Args:
            name (str): The name of the source Rez packge to create.
            text (str): The text that will be used for a "package.py" file.

        Returns:
            :class:`rez.developer_package.DeveloperPackage`:
                The package the represents the newly-built package.

        """
        directory = _make_fake_source_package(name, text)

        package = packages_.get_developer_package(directory)
        new_package = creator.build(package, tempfile.mkdtemp())

        self.add_item(os.path.dirname(directory))
        self.add_item(inspection.get_packages_path_from_package(new_package))

        return new_package
